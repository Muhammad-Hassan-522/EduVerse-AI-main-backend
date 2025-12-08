
from bson import ObjectId
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.db.database import get_courses_collection, get_students_collection, db
from app.schemas.courses import CourseCreate, CourseUpdate

class CourseCRUD:
   
    def __init__(self):
        self.collection = get_courses_collection()
        self.students_collection = get_students_collection()

    def clean_update_data(self, update_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Remove unwanted values from update data before saving to database"""
        cleaned = {}
        
        for key, value in update_dict.items():
            if value is None:
                continue
            
            if isinstance(value, str) and value.strip().lower() == "string":
                continue
            
            if isinstance(value, str) and value.strip() == "" and key != "thumbnailUrl":
                continue
            
            if isinstance(value, list):
                if len(value) > 0 and all(
                    isinstance(item, dict) and 
                    item.get('title', '').strip().lower() == 'string'
                    for item in value
                ):
                    continue
                
                if len(value) == 0 and key != "modules":
                    continue
            
            cleaned[key] = value
        
        return cleaned

    async def create_course(self, course_data: CourseCreate) -> dict:
        """
         UPDATED: Create a new course with validation
        
        Changes made:
        1. Validates that tenant exists in database
        2. Validates that teacher exists and belongs to same tenant
        3. Converts teacherId to ObjectId (was string before)
        4. Updates teacher's assignedCourses array automatically
        
        Raises:
            ValueError: If tenant/teacher not found or validation fails
        """
        course_dict = course_data.dict()
        
        # Validate tenantId format
        if not ObjectId.is_valid(course_dict["tenantId"]):
            raise ValueError(f"Invalid tenant ID format: {course_dict['tenantId']}")
        
        #  Validate teacherId format
        if not ObjectId.is_valid(course_dict["teacherId"]):
            raise ValueError(f"Invalid teacher ID format: {course_dict['teacherId']}")
        
        tenant_id = ObjectId(course_dict["tenantId"])
        teacher_id = ObjectId(course_dict["teacherId"])
        
        # Check if tenant exists in database
        tenant = await db.tenants.find_one({"_id": tenant_id})
        if not tenant:
            raise ValueError(f"Tenant not found with ID: {course_dict['tenantId']}")
        
        #  Check if teacher exists and belongs to the same tenant
        teacher = await db.teachers.find_one({
            "_id": teacher_id,
            "tenantId": tenant_id
        })
        
        if not teacher:
            # Check if teacher exists in a different tenant
            teacher_exists = await db.teachers.find_one({"_id": teacher_id})
            if teacher_exists:
                raise ValueError("Teacher found but belongs to different tenant")
            raise ValueError(f"Teacher not found with ID: {course_dict['teacherId']}")
        
        #  Store both IDs as ObjectId (teacherId was string before)
        course_dict["tenantId"] = tenant_id
        course_dict["teacherId"] = teacher_id
        
        # Add timestamps
        course_dict["createdAt"] = datetime.utcnow()
        course_dict["updatedAt"] = datetime.utcnow()
        course_dict["enrolledStudents"] = 0
        
        # Insert into MongoDB
        result = await self.collection.insert_one(course_dict)
        course_id = result.inserted_id
        
        #  Update teacher's assignedCourses array
        await db.teachers.update_one(
            {"_id": teacher_id},
            {
                "$addToSet": {"assignedCourses": course_id},
                "$set": {"updatedAt": datetime.utcnow()}
            }
        )
        
        # Convert ObjectIds to strings for response
        course_dict["_id"] = str(course_id)
        course_dict["tenantId"] = str(tenant_id)
        course_dict["teacherId"] = str(teacher_id)
        
        return course_dict

    async def get_course_by_id(self, course_id: str, tenantId: str) -> dict:
        """Get a course by ID with proper error handling"""
        
        if not ObjectId.is_valid(course_id):
            return {
                "success": False,
                "message": f"Invalid course ID format: {course_id}",
                "course": None
            }
        
        if not ObjectId.is_valid(tenantId):
            return {
                "success": False,
                "message": f"Invalid tenant ID format: {tenantId}",
                "course": None
            }
        
        # Query with tenantId as ObjectId
        course = await self.collection.find_one({
            "_id": ObjectId(course_id),
            "tenantId": ObjectId(tenantId)
        })
        
        if not course:
            course_exists = await self.collection.find_one({"_id": ObjectId(course_id)})
            
            if course_exists:
                return {
                    "success": False,
                    "message": "Course found but belongs to different tenant",
                    "course": None
                }
            else:
                return {
                    "success": False,
                    "message": f"Course not found with ID: {course_id}",
                    "course": None
                }
        
        # Convert ObjectIds to strings for JSON response
        course["_id"] = str(course["_id"])
        course["tenantId"] = str(course["tenantId"])
        
        #  Handle teacherId as ObjectId (was string before)
        if "teacherId" in course and isinstance(course["teacherId"], ObjectId):
            course["teacherId"] = str(course["teacherId"])
        
        return {
            "success": True,
            "message": "Course retrieved successfully",
            "course": course
        }

    async def get_all_courses(
        self, 
        tenantId: str,
        teacher_id: Optional[str] = None,
        status: Optional[str] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> dict:
        """Get all courses with filters"""
        
        if not ObjectId.is_valid(tenantId):
            return {
                "success": False,
                "message": f"Invalid tenant ID format: {tenantId}",
                "courses": [],
                "total": 0
            }
        
        # Query with tenantId as ObjectId
        query = {"tenantId": ObjectId(tenantId)}
        
        #  Teacher filter now converts to ObjectId (was string before)
        if teacher_id:
            if ObjectId.is_valid(teacher_id):
                query["teacherId"] = ObjectId(teacher_id)
            else:
                return {
                    "success": False,
                    "message": f"Invalid teacher ID format: {teacher_id}",
                    "courses": [],
                    "total": 0
                }
        
        if status:
            status = status.strip()
            query["status"] = {"$regex": f"^{status}$", "$options": "i"}
        
        if category:
            category = category.strip()
            query["category"] = {"$regex": f"^{category}$", "$options": "i"}
        
        if search:
            search = search.strip()
            query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
                {"category": {"$regex": search, "$options": "i"}},
                {"courseCode": {"$regex": search, "$options": "i"}}
            ]
        
        try:
            total = await self.collection.count_documents(query)
            cursor = self.collection.find(query).skip(skip).limit(limit)
            courses = await cursor.to_list(length=limit)
            
            # Convert ObjectIds to strings
            for course in courses:
                course["_id"] = str(course["_id"])
                course["tenantId"] = str(course["tenantId"])
                
                #  Handle teacherId as ObjectId
                if "teacherId" in course and isinstance(course["teacherId"], ObjectId):
                    course["teacherId"] = str(course["teacherId"])
            
            return {
                "success": True,
                "message": f"Found {len(courses)} courses (total: {total})",
                "courses": courses,
                "total": total,
                "skip": skip,
                "limit": limit
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error fetching courses: {str(e)}",
                "courses": [],
                "total": 0
            }

    async def update_course(
        self, 
        course_id: str, 
        tenantId: str, 
        course_update: CourseUpdate
    ) -> Optional[dict]:
        """Update a course with new information"""
        
        if not ObjectId.is_valid(course_id):
            return None
        
        if not ObjectId.is_valid(tenantId):
            return None
        
        update_data = course_update.dict(exclude_unset=True)
        cleaned_data = self.clean_update_data(update_data)
        
        if not cleaned_data:
            result = await self.get_course_by_id(course_id, tenantId)
            return result.get("course") if result["success"] else None
        
        cleaned_data["updatedAt"] = datetime.utcnow()
        
        from pymongo import ReturnDocument
        
        # Update with tenantId as ObjectId
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(course_id), "tenantId": ObjectId(tenantId)},
            {"$set": cleaned_data},
            return_document=ReturnDocument.AFTER
        )
        
        if result:
            result["_id"] = str(result["_id"])
            result["tenantId"] = str(result["tenantId"])
            
            # Handle teacherId as ObjectId
            if "teacherId" in result and isinstance(result["teacherId"], ObjectId):
                result["teacherId"] = str(result["teacherId"])
            
        return result

    

    async def delete_course(self, course_id: str, tenantId: str) -> dict:
     """
    Delete a course and clean up all references
    
    This method:
    1. Validates IDs
    2. Gets the course to find teacher and enrolled students
    3. Deletes the course
    4. Removes from teacher's assignedCourses
    5. Removes from all students' enrolledCourses
    """
    
     if not ObjectId.is_valid(course_id):
        return {
            "success": False, 
            "message": f"Invalid course ID format: {course_id}"
        }
    
     if not ObjectId.is_valid(tenantId):
        return {
            "success": False, 
            "message": f"Invalid tenant ID format: {tenantId}"
        }
    
     course_obj_id = ObjectId(course_id)
     tenant_obj_id = ObjectId(tenantId)
    
    # Get the course first to access teacher ID
     course = await self.collection.find_one({
        "_id": course_obj_id,
        "tenantId": tenant_obj_id
    })
    
     if not course:
        # Check if course exists in different tenant
        course_exists = await self.collection.find_one({"_id": course_obj_id})
        if course_exists:
            return {
                "success": False,
                "message": "Course found but belongs to different tenant"
            }
        return {
            "success": False,
            "message": f"Course not found with ID: {course_id}"
        }
    
    # Get teacher ID before deleting
     teacher_id = course.get("teacherId")
    
    # Delete the course
     delete_result = await self.collection.delete_one({
        "_id": course_obj_id,
        "tenantId": tenant_obj_id
    })
    
     if delete_result.deleted_count > 0:
        #  Remove course from teacher's assignedCourses array
        if teacher_id:
            # Ensure teacher_id is ObjectId
            if isinstance(teacher_id, str):
                teacher_id = ObjectId(teacher_id)
            
            teacher_update_result = await db.teachers.update_one(
                {"_id": teacher_id},
                {
                    "$pull": {"assignedCourses": course_obj_id},
                    "$set": {"updatedAt": datetime.utcnow()}
                }
            )
            
            print(f" Teacher update: Modified {teacher_update_result.modified_count} document(s)")
        
        #  Remove course from all enrolled students' enrolledCourses
        students_update_result = await self.students_collection.update_many(
            {"enrolledCourses": course_id},  # Course ID stored as string in students
            {
                "$pull": {"enrolledCourses": course_id},
                "$set": {"updatedAt": datetime.utcnow()}
            }
        )
        
        print(f" Students update: Modified {students_update_result.modified_count} document(s)")
        
        return {
            "success": True,
            "message": f"Course deleted successfully. Updated {teacher_update_result.modified_count if teacher_id else 0} teacher and {students_update_result.modified_count} students."
        }
    
    # This shouldn't happen, but handle it just in case
     return {
        "success": False,
        "message": "Failed to delete course"
    }

    async def enroll_student(self, course_id: str, student_id: str, tenantId: str) -> dict:
        """Enroll a student in a course"""
        
        if not ObjectId.is_valid(course_id):
            return {"success": False, "message": f"Invalid course ID format: {course_id}"}
        
        if not ObjectId.is_valid(student_id):
            return {"success": False, "message": f"Invalid student ID format: {student_id}"}
        
        if not ObjectId.is_valid(tenantId):
            return {"success": False, "message": f"Invalid tenant ID format: {tenantId}"}
        
        tenant_object_id = ObjectId(tenantId)
        
        # Check course with ObjectId tenantId
        course = await self.collection.find_one({
            "_id": ObjectId(course_id),
            "tenantId": tenant_object_id
        })
        
        if not course:
            course_exists = await self.collection.find_one({"_id": ObjectId(course_id)})
            if course_exists:
                return {"success": False, "message": "Course found but belongs to different tenant"}
            return {"success": False, "message": f"Course not found with ID: {course_id}"}
        
        # Check student with ObjectId tenantId
        student = await self.students_collection.find_one({
            "_id": ObjectId(student_id),
            "tenantId": tenant_object_id
        })
        
        if not student:
            student_exists = await self.students_collection.find_one({"_id": ObjectId(student_id)})
            if student_exists:
                return {"success": False, "message": "Student found but belongs to different tenant"}
            return {"success": False, "message": f"Student not found with ID: {student_id}"}
        
        enrolled_courses = student.get("enrolledCourses", [])
        if course_id in enrolled_courses:
            return {"success": False, "message": "Student is already enrolled in this course"}
        
        await self.students_collection.update_one(
            {"_id": ObjectId(student_id), "tenantId": tenant_object_id},
            {
                "$addToSet": {"enrolledCourses": course_id},
                "$set": {"updatedAt": datetime.utcnow()}
            }
        )
        
        await self.collection.update_one(
            {"_id": ObjectId(course_id), "tenantId": tenant_object_id},
            {
                "$inc": {"enrolledStudents": 1},
                "$set": {"updatedAt": datetime.utcnow()}
            }
        )
        
        return {"success": True, "message": "Successfully enrolled in course"}

    async def unenroll_student(self, course_id: str, student_id: str, tenantId: str) -> dict:
        """
        Unenroll a student from a course
        
        This function:
        1. Validates that both course and student exist
        2. Checks if student is actually enrolled
        3. Removes course from student's enrolledCourses array
        4. Decrements the course's enrolledStudents count
        """
        # Validate course ID format
        if not ObjectId.is_valid(course_id):
            return {"success": False, "message": f"Invalid course ID format: {course_id}"}
        
        # Validate student ID format
        if not ObjectId.is_valid(student_id):
            return {"success": False, "message": f"Invalid student ID format: {student_id}"}
        
        # Validate tenant ID format
        if not ObjectId.is_valid(tenantId):
            return {"success": False, "message": f"Invalid tenant ID format: {tenantId}"}
        
        # Convert tenantId to ObjectId
        tenant_object_id = ObjectId(tenantId)
        
        # Check if course exists (with tenant isolation)
        course = await self.collection.find_one({
            "_id": ObjectId(course_id),
            "tenantId": tenant_object_id
        })
        
        if not course:
            # Check if course exists in a different tenant
            course_exists = await self.collection.find_one({"_id": ObjectId(course_id)})
            if course_exists:
                return {"success": False, "message": "Course found but belongs to different tenant"}
            return {"success": False, "message": f"Course not found with ID: {course_id}"}
        
        # Check if student exists (with tenant isolation)
        student = await self.students_collection.find_one({
            "_id": ObjectId(student_id),
            "tenantId": tenant_object_id
        })
        
        if not student:
            # Check if student exists in a different tenant
            student_exists = await self.students_collection.find_one({"_id": ObjectId(student_id)})
            if student_exists:
                return {"success": False, "message": "Student found but belongs to different tenant"}
            return {"success": False, "message": f"Student not found with ID: {student_id}"}
        
        # Check if student is actually enrolled in this course
        enrolled_courses = student.get("enrolledCourses", [])
        if course_id not in enrolled_courses:
            return {"success": False, "message": "Student is not enrolled in this course"}
        
        # Remove course from student's enrolledCourses array
        await self.students_collection.update_one(
            {"_id": ObjectId(student_id), "tenantId": tenant_object_id},
            {
                "$pull": {"enrolledCourses": course_id},
                "$set": {"updatedAt": datetime.utcnow()}
            }
        )
        
        # Decrement the course's enrolled student count by 1
        await self.collection.update_one(
            {"_id": ObjectId(course_id), "tenantId": tenant_object_id},
            {
                "$inc": {"enrolledStudents": -1},
                "$set": {"updatedAt": datetime.utcnow()}
            }
        )
        
        return {"success": True, "message": "Successfully unenrolled from course"}

    async def get_student_courses(self, student_id: str, tenantId: str) -> dict:
        """Get all courses a student is enrolled in"""
        
        if not ObjectId.is_valid(student_id):
            return {
                "success": False,
                "message": f"Invalid student ID format: {student_id}",
                "courses": []
            }
        
        if not ObjectId.is_valid(tenantId):
            return {
                "success": False,
                "message": f"Invalid tenant ID format: {tenantId}",
                "courses": []
            }
        
        # Query with ObjectId tenantId
        student = await self.students_collection.find_one({
            "_id": ObjectId(student_id),
            "tenantId": ObjectId(tenantId)
        })
        
        if not student:
            student_exists = await self.students_collection.find_one({
                "_id": ObjectId(student_id)
            })
            
            if student_exists:
                return {
                    "success": False,
                    "message": "Student found but belongs to different tenant",
                    "courses": []
                }
            else:
                return {
                    "success": False,
                    "message": f"Student not found with ID: {student_id}",
                    "courses": []
                }
        
        enrolled_courses = student.get("enrolledCourses", [])
        
        if not enrolled_courses or len(enrolled_courses) == 0:
            return {
                "success": True,
                "message": "Student is not enrolled in any courses",
                "courses": []
            }
        
        course_ids = [ObjectId(cid) for cid in enrolled_courses if ObjectId.is_valid(cid)]
        
        if not course_ids:
            return {
                "success": True,
                "message": "Student has invalid course enrollments",
                "courses": []
            }
        
        cursor = self.collection.find({"_id": {"$in": course_ids}})
        courses = await cursor.to_list(length=100)
        
        # Convert ObjectIds to strings
        for course in courses:
            course["_id"] = str(course["_id"])
            course["tenantId"] = str(course["tenantId"])
            
            #  UPDATED: Handle teacherId as ObjectId
            if "teacherId" in course and isinstance(course["teacherId"], ObjectId):
                course["teacherId"] = str(course["teacherId"])
        
        return {
            "success": True,
            "message": f"Found {len(courses)} enrolled courses",
            "courses": courses
        }

# Create a single instance
course_crud = CourseCRUD()