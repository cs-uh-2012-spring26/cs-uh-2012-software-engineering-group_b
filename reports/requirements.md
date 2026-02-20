# requirements.md

---

# Requirements Elicitation and Analysis

## Meeting Information

We met with the client on **February 10th at 2:00 PM** to clarify and refine the requirements for Sprint 1 of the Fitness Class Management and Booking System.

The goal of the meeting was to resolve ambiguities in the high-level user stories and ensure the requirements were precise enough to derive use cases and REST API endpoints .

---

## Elicitation Techniques Used

During the meeting, we used the following techniques:

### 1. Structured Interview

We prepared targeted clarification questions for each feature. The key questions asked included:

### Actors and Roles

* Are the following actors correct: Guest, Member, Trainer, Admin?
* Should any roles be merged or removed?
* Who has permission to create classes?
* Who can view booking lists?

### Feature 1: Create Class

* Who is allowed to create a class (trainer only, admin, or any authenticated user)?
* What information is required? (name, description, date/time, duration, capacity, location)
* Can two classes overlap in time?
* Is capacity mandatory, and what happens when it is reached?
* Can a class be edited or deleted in Sprint 1?

### Feature 2: View Class List

* Should the list include past classes or only upcoming ones?
* What fields must be visible in the list?
* Should filtering or sorting be supported?
* Should unauthenticated users be able to view the class list?

### Feature 3: Book a Class

* Can both guests and members book?
* Can a user book the same class more than once?
* What happens if the class is full?
* Is cancellation supported in Sprint 1?
* Should authentication be required for booking?

### Feature 4: View Member/Guest List

* Who can view the booking list (trainer only, admin only, or both)?
* What booking details should be visible?
* Should this endpoint require authentication?

### Feature 5: Registration and Login (New)

* How do users create an account?
* What validation is required during registration? (Update: Must ensure email and phone number are not duplicated).
* How do users authenticate to receive their token? 

### Authentication and Authorization

* Which features require authentication?
* Should role-based access control be enforced?
* Is simple token-based authentication sufficient for Sprint 1?
* How are roles assigned during registration? (Update: Hard-coded invite tokens will be used to assign Trainer and Admin roles).
* How should the token be formatted in the request headers? (Update: The user must explicitly add "Bearer " before the JWT in the Authorization header).

---

### 2. Scenario-Based Questioning

We discussed both normal flows and edge cases, such as:

* Booking a full class
* Booking a non-existent class
* Duplicate bookings
* Unauthorized access to restricted endpoints
* Missing or invalid input fields
* Registration attempts with an already existing email or phone number.
* Registration attempts with an invalid invite token.
* API requests failing due to a missing "Bearer " prefix in the Authorization header.

---

### 3. Clarification of Assumptions

We explicitly presented our assumptions about:

* Actor permissions
* Role-based access control
* Required input validation
* Authentication requirements

We confirmed these assumptions with the client before finalizing requirements.

---

## Reflection on the Elicitation Process

The structured interview approach was effective because it ensured that each Sprint 1 feature was discussed systematically. The prepared questions helped prevent ambiguity and ensured we covered edge cases and constraints.

Scenario-based questioning was particularly useful in clarifying expected system behavior under exceptional conditions (e.g., full classes, unauthorized users).

In retrospect, bringing a draft UML use case diagram to the meeting would have further improved clarity by visually validating actor-role relationships in real time.

---

## Important Clarification Gained

A key clarification gained during the meeting was that:

* **Trainer and Admin have the same permissions in Sprint 1.**
* Admin accounts will be created using a **token-based mechanism**.
* Role-based access control should be enforced for restricted endpoints.
* Only the CREATE and POST endpoints are needed for sprint 1. There is no need to consider cancellation of the booking, so the DELETE endpoint is not needed for sprint 1.
* Registration must validate that neither the email nor the phone number is duplicated.
* **Viewing the class list is public.** Everybody can view the class list, regardless of authentication status.
* **Strict JWT Formatting:** It must be explained very clearly to consumers of the API that the `Authorization` header requires the exact format: `Bearer <JWT>`. Omitting the "Bearer " prefix will result in an authentication failure.

This clarification significantly impacted the system design by simplifying the permission model and defining how authentication and authorization should be implemented.

---

For the detailed Requirements Specification, including actors, use case diagram, and fleshed-out use cases, see [Requirements-Specification.md](Requirements-Specification.md).
