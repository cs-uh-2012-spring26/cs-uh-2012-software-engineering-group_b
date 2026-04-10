# Design Reflection — Sprint 3A

---

## Executive Summary

To ensure our UML diagrams accurately reflected the system architecture while remaining accessible for technical documentation we adopted a hybrid approach utilizing automated reverse engineering tools followed by manual refinement. For the class diagram we used pyreverse to extract foundational class dependencies from the python codebase and then imported the resulting .dot file into GraphvizOnline to manually clean up dependency edges and logically group our API, Service, and Database layers. Similarly for the sequence diagram we leveraged the PyReverseSequence plugin in VSCode to trace the exact python call stack into base Mermaid syntax. We then ported these raw fragments into the Mermaid Web Editor where we manually injected necessary HTTP boundaries, Client actors, and critical validation gates (such as break and alt blocks) to accurately capture the system's error handling and external service integrations.

| Team Member | Responsibilities |
|-------------|-----------------|
| [Tianze]    | Task 1 creating and explain in depth the class diagrams and sequence diagrams and detailing the executive summary and exploring and documneting new feature foresee for task 4 |
| [Name]      | e.g., Sequence diagrams, Task 2 violations 3–5, Task 3 smells 3–5 |
| [Name]      | e.g., Task 4 reflection, report formatting, review |

---

## Task 1: Design Diagrams

### 1.1 Class Diagram

![Class diagram](class_diagrams\class_diagram.svg)

**Notes and descriptions with key design decisions:**
> This class digram shows the API resources (such as BookingResource and ClassReminderResource) act as controllers that depend on pure function calls (like create_booking()) from the database modules (users, fitness_classes, bookings) rather than using a traditional Object-Oriented ORM. The core data models share standard 1 to 0..n associations, indicating that the independent user and fitness class collections are linked to multiple individual bookings via ID references rather than nested composition. A notable design choice is the decoupling of external integrations instead of sending emails directly the ClassReminderResource delegates the attendee data to the EmailReminderService, which independently manages the external HTTP calls to the SendGridAPI ensuring the core API routing logic remains safely isolated from third-party network dependencies.

---

### 1.2 Sequence Diagram — Book a Class Endpoint


![Book a class sequence diagram](sequence_diagrams\book_a_class_sequence_diagram.png)


**Notes and descriptions:**
> The sequence diagram illustrates the end-to-end execution flow for booking a fitness class, triggered when a Client sends a POST request to the API. The process begins with JWT authentication and proceeds through a series of strict validation gates which clearly modeled using break fragments and will immediately return HTTP error codes (403, 404, 400) if the user identity mismatches, entities are missing, the user lacks member privileges, or a duplicate booking is found. Once these guardrails are cleared, the API constructs the booking document and executes a noteworthy concurrency safe atomic database update to decrement the class's available spots, returning a 409 Conflict if the class is already full. This ensures that the final MongoDB insertion step only occurs when all business rules and capacity constraints are definitively satisfied, ultimately culminating in a 201 Created success response to the Client.

---

### 1.3 Sequence Diagram — Send Reminders Endpoint

![Send class reminder sequence diagram](sequence_diagrams\send_email_reminder_sequence_diagram.png)

**Notes and descriptions:**
> This sequence diagram outlines the execution path for a trainer initiating class reminders starting with role based authorization and proceeding through sequential database queries to fetch class details and attendee bookings. this flow will trigger break fragments that immediately halt execution and return HTTP errors if the class is missing, scheduled in the past, or lacks attendees. Once the data is validated and deduplicated the API deliberately delegates the notification logic to a dedicated email service layer. This will have the service construct the message and loop through unique recipients to dispatch external requests to the SendGrid API. Furthermore the diagram uses a final alt block to ensure that if the external SendGrid network call fails, the system safely catches the exception and returns a 502 Bad Gateway rather than crashing the application.

---

## Task 2: Design Principle Violations

> _Identify **five** places in your code where OO design principles (Abstraction, Encapsulation, Modularity, Hierarchy) or SOLID principles are violated. Aim for at least **three distinct principles**. For each violation, provide: the principle, file name, line numbers, method name, a screenshot, and a clear explanation._

---

### Violation 1 — [Principle Name]

**Principle:** [e.g., Single Responsibility Principle]  
**File:** `path/to/file.py`  
**Lines:** [e.g., 42–78]  
**Method/Class:** `method_or_class_name()`

**Screenshot:**
> _[Insert screenshot of the relevant code here]_

**Explanation:**
> _Explain clearly why this code violates the stated principle. Be specific — reference the code directly._

---

### Violation 2 — [Principle Name]

**Principle:**  
**File:**  
**Lines:**  
**Method/Class:**

**Screenshot:**
> _[Insert screenshot]_

**Explanation:**
> _[Your explanation]_

---

### Violation 3 — [Principle Name]

**Principle:**  
**File:**  
**Lines:**  
**Method/Class:**

**Screenshot:**
> _[Insert screenshot]_

**Explanation:**
> _[Your explanation]_

---

### Violation 4 — [Principle Name]

**Principle:**  
**File:**  
**Lines:**  
**Method/Class:**

**Screenshot:**
> _[Insert screenshot]_

**Explanation:**
> _[Your explanation]_

---

### Violation 5 — [Principle Name]

**Principle:**  
**File:**  
**Lines:**  
**Method/Class:**

**Screenshot:**
> _[Insert screenshot]_

**Explanation:**
> _[Your explanation]_

---

## Task 3: Code Smells

> _Identify at least **five distinct code smell types** in your source code and/or tests. For each, state the smell, the file/line numbers/method name, and include a screenshot._

---

### Code Smell 1 — [Smell Name]

**Smell:** [e.g., Long Method, God Class, Duplicate Code, Feature Envy, etc.]  
**File:** `path/to/file.py`  
**Lines:** [e.g., 101–145]  
**Method/Class:** `method_or_class_name()`

**Screenshot:**
> _[Insert screenshot]_

**Explanation:**
> _Explain why this qualifies as the stated code smell._

---

### Code Smell 2 — [Smell Name]

**Smell:**  
**File:**  
**Lines:**  
**Method/Class:**

**Screenshot:**
> _[Insert screenshot]_

**Explanation:**
> _[Your explanation]_

---

### Code Smell 3 — [Smell Name]

**Smell:**  
**File:**  
**Lines:**  
**Method/Class:**

**Screenshot:**
> _[Insert screenshot]_

**Explanation:**
> _[Your explanation]_

---

### Code Smell 4 — [Smell Name]

**Smell:**  
**File:**  
**Lines:**  
**Method/Class:**

**Screenshot:**
> _[Insert screenshot]_

**Explanation:**
> _[Your explanation]_

---

### Code Smell 5 — [Smell Name]

**Smell:**  
**File:**  
**Lines:**  
**Method/Class:**

**Screenshot:**
> _[Insert screenshot]_

**Explanation:**
> _[Your explanation]_

---

## Task 4: Reflection on New Features

> _Reflect on how your current design will **help or hinder** the implementation of the two new features below, with particular attention to **maintainability** and **extensibility**._

### New Features

- **Feature 6 — Create Recurring Class:** As a trainer, I want to create recurring classes (e.g., daily or monthly) so that I don't have to manually re-enter the same class multiple times.
- **Feature 7 — Configure Notifications:** As someone registered in a class, I want to choose how I receive reminders (e.g., email and/or Telegram and/or SMS) so I can stay informed in the ways that suit me.

---

### 4.1 Feature 6 — Create Recurring Class

**How does the current design help?**
> Our current modular database layer isolates data construction from persistence. Because we have pure functions like build_fitness_class_document() and generate_fitness_class_id() in fitness_classes.py, programmatically generating multiple instances of a class for future dates will be straightforward without needing to duplicate raw dictionary creation logic.

**How does the current design hinder?**
>The current database schema is entirely flat and treats every fitness class as a standalone entity. There is no concept of a "Series" or "Template" which relates to poor abstraction. so if a trainer creates a daily class for a month and then needs to change the time or cancel the series, they would have to update 30 independent documents. Furthermore, our current create_fitness_class function uses insert_one which means batch creation would require looping network calls which is inefficient and could fail mid-loop.

**Initial thoughts on approach:**
> We could modify the fitness_classes schema to include an optional series_id or recurrence_rule field to link recurring instances together. Alternatively we could also introduce a ClassTemplate entity. On the database layer we should introduce a bulk_create_fitness_classes() function utilizing MongoDB's insert_many for atomic efficient batch processing therefore solving the issue of having the ability to only create one class at a time.

---

### 4.2 Feature 7 — Configure Notifications

**How does the current design help?**
> The current system already enforces a clean separation of concerns by delegating the actual dispatching of messages out of the API router and into a dedicated service layer (email_reminders.py). This prevents the controller from being bogged down with network logic.

**How does the current design hinder?**
> The design heavily violates the Open Closed Principle and suffers from tight coupling. In ClassReminderResource.post(), the API explicitly iterates through bookings to extract specifically USER_EMAIL and passes it to an explicitly named send_class_reminders function. If we add SMS or Telegram, we will be forced to modify the API controller, the booking schema, and write entirely new conditional service logic. Our current service is also hardcoded specifically for SendGrid API data structures.

**Initial thoughts on approach:**
> First the users schema must be updated to store a notification_preferences field (e.g. {"email": true, "sms": false}). Second, we could implement the Strategy Design Pattern. We would create a generic NotificationManager interface that takes a user's preferences and dynamically delegates the payload to an EmailStrategy, SMSStrategy, or TelegramStrategy. The API endpoint would simply pass a list of user IDs to the manager entirely decoupling the API from the notification medium.

---

### 4.3 Summary

> Overall, our current modular architecture successfully handles basic CRUD operations and enforces basic separation of concerns. However, our design analysis reveals that the system is highly rigid and tailored to a single, flat use case. The lack of relational abstractions (hindering recurring classes) and tight coupling to specific implementations like Email (violating the Open-Closed Principle) will make new features difficult to add safely. Before beginning Sprint 3B, our priority must be refactoring our service layer to use polymorphic design patterns (like Strategy) and extending our data models to support linked entities and user preferences.