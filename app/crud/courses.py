
from bson import ObjectId
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.db.database import get_courses_collection, get_students_collection
from app.schemas.courses import CourseCreate, CourseUpdate

class CourseCRUD:
   
    def __init__(self):
        # Initialize database collections
        self.collection = get_courses_collection()
        self.students_collection = get_students_collection()

    def clean_update_data(self, update_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove unwanted values from update data before saving to database
        
        This function filters out:
        - None values (fields not set)
        - Empty strings (except thumbnailUrl which can be intentionally empty)
        - The literal string "string" (default placeholder from Swagger/API docs)
        - Empty lists (except modules which can be intentionally empty)
        - Lists containing only placeholder data
        
        Args:
            update_dict: Dictionary containing fields to update
            
        Returns:
            Cleaned dictionary with only valid values to update
        """
        cleaned = {}
        
        for key, value in update_dict.items():
            # Skip if value is None (field not provided)
            if value is None:
                continue
            
            # Skip if value is the placeholder string "string" from Swagger
            if isinstance(value, str) and value.strip().lower() == "string":
                continue
            
            # Skip empty strings (but allow empty thumbnailUrl)
            if isinstance(value, str) and value.strip() == "" and key != "thumbnailUrl":
                continue
            
            # Handle list fields (like modules)
            if isinstance(value, list):
                # Skip if list contains only placeholder modules with "string" values
                if len(value) > 0 and all(
                    isinstance(item, dict) and 
                    item.get('title', '').strip().lower() == 'string'
                    for item in value
                ):
                    continue
                
                # Skip empty lists (but allow empty modules array)
                if len(value) == 0 and key != "modules":
                    continue
            
            # Value is valid, include it in update
            cleaned[key] = value
        
        return cleaned

    async def create_course(self, course_data: CourseCreate) -> dict:
       
        # Convert Pydantic model to dictionary
        course_dict = course_data.dict()
        
        # Add timestamps
        course_dict["createdAt"] = datetime.utcnow()
        course_dict["updatedAt"] = datetime.utcnow()
        
        # Initialize enrollment count to 0
        course_dict["enrolledStudents"] = 0
        
        # Insert into MongoDB
        result = await self.collection.insert_one(course_dict)
        
        # Add the MongoDB _id to the response
        course_dict["_id"] = str(result.inserted_id)
        
        return course_dict

    async def get_course_by_id(self, course_id: str, tenantId: str) -> Optional[dict]:
      
        # Validate that course_id is a valid MongoDB ObjectId
        if not ObjectId.is_valid(course_id):
            return None
        
        # Find course by ID and tenant (ensures tenant isolation)
        course = await self.collection.find_one({
            "_id": ObjectId(course_id),
            "tenantId": tenantId
        })
        
        # Convert ObjectId to string for JSON serialization
        if course:
            course["_id"] = str(course["_id"])
            
        return course

    async def get_all_courses(
        self, 
        tenantId: str,
        teacher_id: Optional[str] = None,
        status: Optional[str] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[dict]:
        
        # Start with base query - always filter by tenant
        query = {"tenantId": tenantId}
        
        # Add teacher filter if provided
        if teacher_id:
            query["teacherId"] = teacher_id
        
        # Add status filter if provided (remove whitespace)
        if status:
            query["status"] = status.strip()
        
        # Add category filter if provided (remove whitespace)
        if category:
            query["category"] = category.strip()
        
        # Add search filter if provided (searches across multiple fields)
        if search:
            search = search.strip()
            query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},        # Case-insensitive search in title
                {"description": {"$regex": search, "$options": "i"}},  # Case-insensitive search in description
                {"category": {"$regex": search, "$options": "i"}}      # Case-insensitive search in category
            ]
        
        # Execute query with pagination
        cursor = self.collection.find(query).skip(skip).limit(limit)
        courses = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string for all courses
        for course in courses:
            course["_id"] = str(course["_id"])
        
        return courses

    async def update_course(
        self, 
        course_id: str, 
        tenantId: str, 
        course_update: CourseUpdate
    ) -> Optional[dict]:
        """
        Update a course with new information
        
        Only updates fields that are provided in the request.
        Automatically filters out placeholder values and empty fields.
        
        Args:
            course_id: MongoDB ObjectId of the course to update
            tenantId: Tenant ID for multi-tenant isolation
            course_update: Fields to update (only provided fields will be updated)
            
        Returns:
            Updated course document if successful, None if course not found
        """
        # Validate course ID format
        if not ObjectId.is_valid(course_id):
            return None
        
        # Get only fields that were explicitly provided in the request
        # exclude_unset=True means only fields the user actually sent are included
        update_data = course_update.dict(exclude_unset=True)
        
        # Clean the data to remove placeholder values and empty fields
        cleaned_data = self.clean_update_data(update_data)
        
        # If nothing to update after cleaning, return current course as-is
        if not cleaned_data:
            return await self.get_course_by_id(course_id, tenantId)
        
        # Always update the "updatedAt" timestamp
        cleaned_data["updatedAt"] = datetime.utcnow()
        
        # Update the course and return the complete updated document
        from pymongo import ReturnDocument
        
        result = await self.collection.find_one_and_update(
            # Find course by ID and tenant
            {"_id": ObjectId(course_id), "tenantId": tenantId},
            # Update the specified fields
            {"$set": cleaned_data},
            # Return the document AFTER update (not before)
            return_document=ReturnDocument.AFTER
        )
        
        # Convert ObjectId to string if course was found and updated
        if result:
            result["_id"] = str(result["_id"])
            
        return result

    async def delete_course(self, course_id: str, tenantId: str) -> bool:
       
        # Validate course ID format
        if not ObjectId.is_valid(course_id):
            return False
        
        # Delete course (only if it belongs to the correct tenant)
        result = await self.collection.delete_one({
            "_id": ObjectId(course_id),
            "tenantId": tenantId
        })
        
        # Return True if a document was deleted
        return result.deleted_count > 0

    async def enroll_student(self, course_id: str, student_id: str, tenantId: str) -> dict:
        """
        Enroll a student in a course
        
        This function:
        1. Validates that both course and student exist
        2. Checks if student is already enrolled
        3. Adds course to student's enrolledCourses array
        4. Increments the course's enrolledStudents count
        
        Args:
            course_id: ID of the course to enroll in
            student_id: ID of the student to enroll
            tenantId: Tenant ID for multi-tenant isolation
            
        Returns:
            Dictionary with success status and message
        """
        # Validate course ID format
        if not ObjectId.is_valid(course_id):
            return {"success": False, "message": f"Invalid course ID format: {course_id}"}
        
        # Validate student ID format
        if not ObjectId.is_valid(student_id):
            return {"success": False, "message": f"Invalid student ID format: {student_id}"}
        
        # Check if course exists (with tenant isolation)
        course = await self.collection.find_one({
            "_id": ObjectId(course_id),
            "tenantId": tenantId
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
            "tenantId": tenantId
        })
        if not student:
            # Check if student exists in a different tenant
            student_exists = await self.students_collection.find_one({"_id": ObjectId(student_id)})
            if student_exists:
                return {"success": False, "message": "Student found but belongs to different tenant"}
            return {"success": False, "message": f"Student not found with ID: {student_id}"}
        
        # Check if student is already enrolled in this course
        enrolled_courses = student.get("enrolledCourses", [])
        if course_id in enrolled_courses:
            return {"success": False, "message": "Student is already enrolled in this course"}
        
        # Add course to student's enrolledCourses array (won't add duplicates due to $addToSet)
        await self.students_collection.update_one(
            {"_id": ObjectId(student_id), "tenantId": tenantId},
            {"$addToSet": {"enrolledCourses": course_id}}
        )
        
        # Increment the course's enrolled student count by 1
        await self.collection.update_one(
            {"_id": ObjectId(course_id), "tenantId": tenantId},
            {"$inc": {"enrolledStudents": 1}}
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
        
        Args:
            course_id: ID of the course to unenroll from
            student_id: ID of the student to unenroll
            tenantId: Tenant ID for multi-tenant isolation
            
        Returns:
            Dictionary with success status and message
        """
        # Validate course ID format
        if not ObjectId.is_valid(course_id):
            return {"success": False, "message": f"Invalid course ID format: {course_id}"}
        
        # Validate student ID format
        if not ObjectId.is_valid(student_id):
            return {"success": False, "message": f"Invalid student ID format: {student_id}"}
        
        # Check if course exists
        course = await self.collection.find_one({
            "_id": ObjectId(course_id),
            "tenantId": tenantId
        })
        if not course:
            return {"success": False, "message": f"Course not found with ID: {course_id}"}
        
        # Check if student exists
        student = await self.students_collection.find_one({
            "_id": ObjectId(student_id),
            "tenantId": tenantId
        })
        if not student:
            return {"success": False, "message": f"Student not found with ID: {student_id}"}
        
        # Check if student is actually enrolled in this course
        enrolled_courses = student.get("enrolledCourses", [])
        if course_id not in enrolled_courses:
            return {"success": False, "message": "Student is not enrolled in this course"}
        
        # Remove course from student's enrolledCourses array
        await self.students_collection.update_one(
            {"_id": ObjectId(student_id), "tenantId": tenantId},
            {"$pull": {"enrolledCourses": course_id}}
        )
        
        # Decrement the course's enrolled student count by 1
        await self.collection.update_one(
            {"_id": ObjectId(course_id), "tenantId": tenantId},
            {"$inc": {"enrolledStudents": -1}}
        )
        
        return {"success": True, "message": "Successfully unenrolled from course"}

    async def get_student_courses(self, student_id: str, tenantId: str) -> List[dict]:
       
        # Validate student ID format
        if not ObjectId.is_valid(student_id):
            return []
        
        # Find the student
        student = await self.students_collection.find_one({
            "_id": ObjectId(student_id),
            "tenantId": tenantId
        })
        
        # If student not found or has no enrolled courses, return empty list
        if not student or "enrolledCourses" not in student:
            return []
        
        # Convert course ID strings to ObjectIds (only valid ones)
        course_ids = [ObjectId(cid) for cid in student["enrolledCourses"] if ObjectId.is_valid(cid)]
        
        # Find all courses with IDs in the student's enrolledCourses array
        cursor = self.collection.find({"_id": {"$in": course_ids}})
        courses = await cursor.to_list(length=100)
        
        # Convert ObjectId to string for all courses
        for course in courses:
            course["_id"] = str(course["_id"])
        
        return courses

# Create a single instance to be used throughout the application
course_crud = CourseCRUD()