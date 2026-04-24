# Redesign Report — Sprint 3B

## Team Responsibilities
Each member was responsible for specific tasks during Sprint 3B, while maintaining a shared understanding of the overall system redesign and construction:

* **Tianze:** * **Task 1:** Redesign and Refactor (Owned the backend/domain refactoring execution).
  * **Task 5:** Diagrams and Documentation (Updated the class diagrams, authored the `redesign.md` document, and updated README/Swagger docs).
* **Juan:** * **Task 2:** Implemented new features, acting as the lead for **Feature 7** (Configurable Notifications via Email + Telegram using an extensible design).
  * **Task 4:** Ensured Continuous Integration (CI) worked correctly (Push/PR triggers, secrets configuration, passing workflows).
* **Vladimir:** * **Task 1:** Redesign and Refactor (Shared ownership of the backend/domain refactoring).
  * **Task 2:** Implemented new features, acting as the lead for **Feature 6** (Recurring Classes).

---

## Task 1: Refactoring Design Principles and Code Smells

Below is a brief explanation of how we resolved the 10 specific design violations and code smells identified in S3A.

### 1. Fixed Single Responsibility Principle (SRP) in `Register.post`
* **The Fix:** We extracted all password hashing, user validation, and database insertion logic out of the `app/apis/auth.py` controller. 
* **New Structure:** We created `app/services/auth_service.py` featuring a `register_user(data)` function. The API controller now purely handles HTTP request/response routing, completely separating HTTP concerns from domain logic.

### 2. Fixed Open–Closed Principle (OCP) in Invite Tokens
* **The Fix:** We removed the hard-coded `VALID_TOKENS` dictionary from the API layer.
* **New Structure:** Token validation was encapsulated behind a `resolve_registration_role(token)` interface in `auth_service.py`. The system is now open for extension (we can easily switch to a database-backed token system) without modifying the API layer.

### 3. Fixed API-to-DB Coupling (Separation of Concerns)
* **The Fix:** `BookingResource` and `ClassListResource` were directly calling database functions like `decrement_available_spot`.
* **New Structure:** We introduced a formal Service Layer (`booking_service.py` and `fitness_class_service.py`). The controllers now pass payloads to the services, which safely orchestrate the database interactions, strictly enforcing a Layered Architecture.

### 4. Fixed Immutability Side Effects in `utils.py`
* **The Fix:** The `serialize_item` function was mutating the database dictionary reference in place, which is functionally impure.
* **New Structure:** We updated the function to use `new_item = item.copy()`. It now returns a brand new dictionary, preventing unexpected side effects for caller variables.

### 5. Fixed Catch-All Exception Handler in `__init__.py`
* **The Fix:** The application previously caught the base `Exception` class for all errors, masking infrastructure bugs as standard HTTP 500s.
* **New Structure:** We replaced `@api.errorhandler(Exception)` with a specific `@api.errorhandler(DomainValidationError)`. This allows domain rules to return clean 400-level errors while true system bugs fail loudly.

### 6. Fixed "Long Method" Smell in Class Creation
* **The Fix:** `ClassListResource.post` was over 50 lines long, handling datetime parsing, validation, and database formatting.
* **New Structure:** This logic was extracted into a highly cohesive `create_new_class` function in `fitness_class_service.py`, significantly reducing cognitive load in the controller.

### 7. Fixed "Duplicate Code" Smell in Tests
* **The Fix:** The `sample_member1` and `sample_member2` fixtures shared identical login/registration logic.
* **New Structure:** We extracted the shared API testing logic into a parameterized `register_and_login_helper(client, user_data)` function in `test_booking_api.py`.

### 8. Fixed "Dead Code" Smell in `booking.py`
* **The Fix:** There was an unused import (`get_user_by_user_id`).
* **New Structure:** The import was cleanly removed, reducing namespace clutter.

### 9 & 10. Fixed "Long Parameter List" and "Primitive Obsession" in `bookings.py`
* **The Fix:** `build_booking_document` previously took 6 raw string/integer parameters, making argument ordering fragile.
* **New Structure:** We introduced a Data Transfer Object (DTO) via Python's `@dataclass` called `BookingRequest`. The function now takes a single, strongly-typed object.

---

## Task 2: Design Patterns Used for New Features

### Pattern: Strategy Design Pattern 
**Feature:** Feature 7 — Configurable Notifications (Email + Telegram)

**Why it is applicable:** Feature 7 requires the system to send class reminders via different mediums depending on user preferences. If we implemented this sequentially (e.g., a massive `if user_wants_email: ... elif user_wants_telegram: ...` block inside the controller), our code would become tightly coupled to specific third-party APIs and would immediately violate the Open-Closed Principle every time we wanted to add a new notification type (like SMS or Push). 

The **Strategy Pattern** is perfectly applicable here because it allows us to define a family of algorithms (notification methods), encapsulate each one in its own class, and make them interchangeable at runtime based on the user's preference payload.

**How we refactored the system to use it:**
1. **The Interface:** We defined a common `NotificationStrategy` interface (or abstract base class) that requires a `send(recipient, message)` method.
2. **Concrete Strategies:** We created specific implementations: `EmailNotificationStrategy` (which houses the SendGrid API logic) and `TelegramNotificationStrategy` (which houses the Telegram Bot API logic).
3. **The Context/Manager:** We refactored `send_class_reminders` into a `NotificationManager`. When a class reminder is triggered, the manager loops through the attendees, checks their stored preferences, and dynamically instantiates the correct strategy at runtime. 
4. **The Result:** The core application logic no longer knows *how* an email or Telegram message is sent. If we need to add SMS notifications in S3C, we simply create an `SMSNotificationStrategy` without touching any of the existing API or Manager code.