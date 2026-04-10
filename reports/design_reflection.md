# Design Reflection — Sprint 3A

---

## Executive Summary

> _Describe how your team approached this deliverable. Include:_
> - _Tools used (e.g., pyreverse, VS PyReverseSequence Plugin, SonarQube — or state "none" if no tools were used)_
> - _Manual analysis performed and how it was divided_
> - _Each team member's responsibilities_

| Team Member | Responsibilities |
|-------------|-----------------|
| [Tianze]    | [Task 1 creating the class diagrams and sequence diagrams and detailing the executive summary] |
| [Name]      | [e.g., Sequence diagrams, Task 2 violations 3–5, Task 3 smells 3–5] |
| [Name]      | [e.g., Task 4 reflection, report formatting, review] |

---

## Task 1: Design Diagrams

### 1.1 Class Diagram

> _Insert your class diagram here. Show all main classes and their associations (inheritance, composition, aggregation, dependency, etc.). Refine any auto-generated output so it is readable and meaningful._

```
[Insert class diagram image or PlantUML/Mermaid source here]
```

**Notes and descriptions with key design decisions:**
> _Briefly explain any non-obvious associations or design choices shown in the diagram._

---

### 1.2 Sequence Diagram — Book a Class Endpoint

> _Insert a sequence diagram capturing the current control flow for the "book a class" endpoint. Include all relevant actors, objects, and method calls._

```
[Insert sequence diagram image or PlantUML/Mermaid source here]
```

**Notes and descriptions:**
> _Briefly describe the flow shown and highlight anything noteworthy._

---

### 1.3 Sequence Diagram — Send Reminders Endpoint

> _Insert a sequence diagram capturing the current control flow for the "send reminders" endpoint. Include all relevant actors, objects, and method calls._

```
[Insert sequence diagram image or PlantUML/Mermaid source here]
```

**Notes and descriptions:**
> _Briefly describe the flow shown and highlight anything noteworthy._

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

### Code Smell 1 — Long Method

**Smell:** Long Method, God Class  
**File:** `app/apis/fitness_class.py`  
**Lines:** 91-144  
**Method/Class:** `ClassListResource.post()`

**Screenshot:**
![Code Smell 1](images/code_smell_1.png)

**Explanation:**
> The `post()` method handles many responsibilities in one place: payload extraction, validation, datetime parsing, business rule checks (past date and duplicates), response construction, and persistence. This increases cognitive load and makes future feature additions (e.g., recurring classes) harder to implement safely.

---

### Code Smell 2 — Duplicate Code

**Smell:** Duplicate Code  
**File:** `tests/unit/test_booking_api.py`  
**Lines:** 36-57 and 60-81  
**Method/Class:** `sample_member1()` and `sample_member2()` fixtures

**Screenshot:**
![Code Smell 2](images/code_smell_2.png)

**Explanation:**
> Both fixtures repeat almost the same registration and token fallback logic with only small literal changes (email/phone/password/name). This duplication makes test maintenance harder and increases the chance of inconsistent behavior when the auth flow changes.

---

### Code Smell 3 — Dead Code (Unused Import)

**Smell:** Dead Code / Unused Import  
**File:** `app/apis/booking.py`  
**Lines:** 25-34 (specifically line 33)  
**Method/Class:** module-level imports

**Screenshot:**
![Code Smell 3](images/code_smell_3.png)

**Explanation:**
> `get_user_by_user_id` is imported but never used in this module. Unused imports are a maintainability smell because they add noise, can mislead readers about dependencies, and often indicate leftover code from previous refactors.

---

### Code Smell 4 — Long Parameter List

**Smell:** Long Parameter List  
**File:** `app/db/bookings.py`  
**Lines:** 37-48  
**Method/Class:** `build_booking_document()`

**Screenshot:**
![Code Smell 4](images/code_smell_4.png)

**Explanation:**
> `build_booking_document()` takes many primitive parameters (`class_id`, `user_id`, `user_name`, `user_email`, `phone`, `role`, plus optional fields). This is a long parameter list smell because it increases call-site complexity and makes argument ordering/consistency errors more likely as the booking model evolves.

---

### Code Smell 5 — Primitive Obsession

**Smell:** Primitive Obsession  
**File:** `app/db/bookings.py`  
**Lines:** 13-25 and 37-62  
**Method/Class:** `build_booking_document()`

**Screenshot:**
![Code Smell 5](images/code_smell_5.png)

**Explanation:**
> Booking domain concepts are represented as raw primitives (multiple strings for `role`, `status`, `user_email`, `class_id`, etc.) instead of richer domain types or value objects. This makes invalid states easier to pass around and spreads format/validation concerns across the codebase.

---

## Task 4: Reflection on New Features

> _Reflect on how your current design will **help or hinder** the implementation of the two new features below, with particular attention to **maintainability** and **extensibility**._

### New Features

- **Feature 6 — Create Recurring Class:** As a trainer, I want to create recurring classes (e.g., daily or monthly) so that I don't have to manually re-enter the same class multiple times.
- **Feature 7 — Configure Notifications:** As someone registered in a class, I want to choose how I receive reminders (e.g., email and/or Telegram and/or SMS) so I can stay informed in the ways that suit me.

---

### 4.1 Feature 6 — Create Recurring Class

**How does the current design help?**
> _[Describe any existing abstractions, patterns, or structures that would make this easier to implement.]_

**How does the current design hinder?**
> _[Reference specific violations or smells from Tasks 2 & 3 that would make this harder. Discuss maintainability/extensibility concerns.]_

**Initial thoughts on approach:**
> _[High-level thoughts on how you might redesign or extend the system to support this feature cleanly — no implementation required.]_

---

### 4.2 Feature 7 — Configure Notifications

**How does the current design help?**
> _[Describe any existing abstractions, patterns, or structures that would make this easier to implement.]_

**How does the current design hinder?**
> _[Reference specific violations or smells from Tasks 2 & 3 that would make this harder. Discuss maintainability/extensibility concerns.]_

**Initial thoughts on approach:**
> _[High-level thoughts on how you might redesign or extend the system to support this feature cleanly — no implementation required.]_

---

### 4.3 Summary

> _Provide a brief overall summary of the team's key takeaways from this design analysis sprint, and what you would prioritise fixing before implementing the new features._