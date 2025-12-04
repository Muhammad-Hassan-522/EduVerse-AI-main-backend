

from bson import ObjectId
from app.db.database import student_performance_collection


# ----------------------- FIX OBJECT IDS (GLOBAL HELPER) ----------------------- #
def fix_object_ids(data):
    """Recursively convert ALL ObjectId inside any dict or list."""

    if isinstance(data, ObjectId):
        return str(data)

    elif isinstance(data, list):
        return [fix_object_ids(item) for item in data]

    elif isinstance(data, dict):
        new_dict = {}
        for key, value in data.items():
            new_dict[key] = fix_object_ids(value)
        return new_dict

    else:
        return data




class StudentPerformanceCRUD:

    # ---------------- XP + LEVEL SYSTEM ---------------- #
    @staticmethod
    def _update_level_system(data: dict):
        xp = data.get("xp", 0)
        level = data.get("level", 1)

        xp_required = level * 500

        while xp >= xp_required:
            xp -= xp_required
            level += 1
            xp_required = level * 500

        data["xp"] = xp
        data["level"] = level
        data["xpToNextLevel"] = xp_required
        return data

    # ---------------- GET BY TENANT ---------------- #
    @staticmethod
    async def get_by_tenant(tenant_id: str):
        doc = await student_performance_collection.find_one(
            {"tenantId": ObjectId(tenant_id)}
        )
        if doc:
            doc["id"] = str(doc["_id"])
            doc["tenantId"] = str(doc["tenantId"])
        return doc

    # ---------------- ADD POINTS + UPDATE XP/LEVEL ---------------- #
    @staticmethod
    async def add_points(tenant_id: str, points: int):

        await student_performance_collection.update_one(
            {"tenantId": ObjectId(tenant_id)},
            {"$inc": {"totalPoints": points, "pointsThisWeek": points, "xp": points}},
        )

        data = await StudentPerformanceCRUD.get_by_tenant(tenant_id)
        if not data:
            return None

        updated_data = StudentPerformanceCRUD._update_level_system(data)

        await student_performance_collection.update_one(
            {"tenantId": ObjectId(tenant_id)},
            {
                "$set": {
                    "xp": updated_data["xp"],
                    "level": updated_data["level"],
                    "xpToNextLevel": updated_data["xpToNextLevel"]
                }
            }
        )

        return updated_data

    # ---------------- WEEKLY STUDY TIME ---------------- #
    @staticmethod
    async def add_weekly_time(tenant_id: str, week_start, minutes: int):
        await student_performance_collection.update_one(
            {"tenantId": ObjectId(tenant_id)},
            {"$push": {"weeklyStudyTime": {"weekStart": week_start, "minutes": minutes}}},
        )
        return await StudentPerformanceCRUD.get_by_tenant(tenant_id)

    # ---------------- BADGES ---------------- #
    @staticmethod
    async def add_badge(tenant_id: str, badge: dict):
        await student_performance_collection.update_one(
            {"tenantId": ObjectId(tenant_id)},
            {"$push": {"badges": badge}},
        )
        return await StudentPerformanceCRUD.get_by_tenant(tenant_id)

    @staticmethod
    async def remove_badge(tenant_id: str, title: str):
        await student_performance_collection.update_one(
            {"tenantId": ObjectId(tenant_id)},
            {"$pull": {"badges": {"title": title}}},
        )
        return await StudentPerformanceCRUD.get_by_tenant(tenant_id)

    # -------------------- TOP 5 LEADERBOARD -------------------- #
    @staticmethod
    async def get_top5_leaderboard():
        cursor = student_performance_collection.find({})
        all_students = await cursor.to_list(length=None)

        if not all_students:
            return []

        leaderboard_entries = []

        for s in all_students:

            # Fix ObjectIds
            s = fix_object_ids(s)

            # Extract from LeaderBoard array (THIS IS WHERE YOUR DATA IS)
            lb_items = s.get("LeaderBoard", [])

            for item in lb_items:
                name = item.get("studentName")
                pts = item.get("points", 0)

                if name:
                    leaderboard_entries.append({
                        "studentName": name,
                        "points": pts
                    })

        # Sort by points descending
        leaderboard_entries.sort(key=lambda x: -x["points"])

        # Take top 5
        top5 = leaderboard_entries[:5]

        # Add ranks
        for i, entry in enumerate(top5, start=1):
            entry["rank"] = i

        return top5


    # ---------------- FULL LEADERBOARD (SORTED + RANKED) ---------------- #
    @staticmethod
    async def get_full_leaderboard():
        cursor = student_performance_collection.find({})
        all_students = await cursor.to_list(length=None)

        if not all_students:
            return []

        cleaned = []
        for s in all_students:
            s = fix_object_ids(s)
            s["id"] = str(s.get("_id"))
            s["tenantId"] = str(s.get("tenantId"))
            s["totalPoints"] = s.get("totalPoints", 0)
            s["xp"] = s.get("xp", 0)
            s["level"] = s.get("level", 1)
            cleaned.append(s)

        cleaned.sort(
            key=lambda x: (-x["totalPoints"], -x["xp"], -x["level"])
        )

        for i, s in enumerate(cleaned, start=1):
            s["rank"] = i

        return cleaned

    # ---------------- CERTIFICATES ---------------- #
    @staticmethod
    async def add_certificate(tenant_id: str, cert: dict):
        await student_performance_collection.update_one(
            {"tenantId": ObjectId(tenant_id)},
            {"$push": {"certificates": cert}},
        )
        return await StudentPerformanceCRUD.get_by_tenant(tenant_id)

    @staticmethod
    async def remove_certificate(tenant_id: str, title: str):
        await student_performance_collection.update_one(
            {"tenantId": ObjectId(tenant_id)},
            {"$pull": {"certificates": {"title": title}}},
        )
        return await StudentPerformanceCRUD.get_by_tenant(tenant_id)
# ---------------- COURSE PROGRESS (SAFE) ---------------- #
    @staticmethod
    async def update_course_progress(tenant_id: str, course_id: str, completion: int, last_active):

        # Try to update existing course progress entry
        update_result = await student_performance_collection.update_one(
            {
                "tenantId": ObjectId(tenant_id),
                "courseStats.courseId": course_id
            },
            {
                "$set": {
                    "courseStats.$.completionPercentage": completion,
                    "courseStats.$.lastActive": last_active
                }
            }
        )

        # If no existing entry was updated → add new course progress
        if update_result.modified_count == 0:
            await student_performance_collection.update_one(
                {"tenantId": ObjectId(tenant_id)},
                {
                    "$push": {
                        "courseStats": {
                            "courseId": course_id,
                            "completionPercentage": completion,
                            "lastActive": last_active
                        }
                    }
                }
            )

        return await StudentPerformanceCRUD.get_by_tenant(tenant_id)

    # -------------- GET COURSE STATS -------------- #
    @staticmethod
    async def get_course_stats(tenant_id: str):
        doc = await student_performance_collection.find_one(
            {"tenantId": ObjectId(tenant_id)},
            {"courseStats": 1, "_id": 0}
        )
        return doc or {"courseStats": []}