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