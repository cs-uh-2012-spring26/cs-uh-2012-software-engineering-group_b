# Requirements Specification

---

# Actors

Based on the meeting, the system has the following actors:

* **Guest**
* **Member**
* **Trainer**
* **Admin**

### Role Clarifications

* Everybody (Guests, Members, Trainers, Admins) can view the class list.
* Members can book classes. Guests can view classes but must register to book.
* Trainers can create classes.
* Admins have the same permissions as Trainers.
* Admin accounts are created via a token mechanism.
* Role-based authentication is enforced for restricted endpoints via JWT claims.

---

# Use Case Diagram

## Textual Representation

Actors and Use Cases:

* Guest → View Class List, Register
* Member → login, View Class List, Book Class
* Trainer → Validate Invite Token, login, View, Class List, Create Class, View Booking List
* Admin → Validate Invite Token, login, View, Class List, Create Class, View Booking List

## Diagram

![Use Case Diagram](uml/main-uml.svg)

---

# Use Case 1: Create Class

## Use Case Name

Create Fitness Class

## Primary Actor

Trainer (Admin has same permissions)

## Preconditions

* User is authenticated.
* User has role Trainer or Admin.
* Required class information is provided.

## Main Success Scenario

1. Actor sends a request to create a new class.
2. System validates input fields.
3. System stores the class in the database.
4. System returns confirmation with class details.

## Alternative Flows

* **Missing Required Fields:**
  System returns 400 Bad Request.

* **Unauthorized User:**
  System returns 403 Forbidden.

## Postconditions

* New class is stored in the system.
* Class is visible in the class list.
* The class is available for members to book.

---

# Use Case 2: View Class List

## Use Case Name

View Class List

## Primary Actor

Guest, Member

## Preconditions

* None

## Main Success Scenario

1. Actor requests list of classes.
2. System retrieves classes from the database.
3. System returns list including:

   * Class name
   * Date/time
   * Capacity
   * Available spots
   * Trainer name

## Alternative Flows

* **No Classes Available:**
  System returns empty list.

## Postconditions

* Actor receives accurate list of classes.

---

# Use Case 3: Book Class

## Use Case Name

Book Fitness Class

## Primary Actor

Member

## Preconditions

* Class exists.
* Class is not full.
* User is authenticated as a Member.
* Class is not already booked by the User.

## Main Success Scenario

1. Actor selects a class.
2. System checks availability.
3. System creates booking entry.
4. System decreases available capacity.
5. System confirms booking.

## Alternative Flows

* **Class Full:**
  System returns error message.

* **Duplicate Booking Attempt:**
  System rejects duplicate booking.

* **Class Does Not Exist:**
  System returns 404 Not Found.

## Postconditions

* Booking is stored.
* Capacity is updated.
* The system updates the user’s booking records to include the selected class.
---

# Use Case 4: View Member/Guest List

## Use Case Name

View Booking List for a Class

## Primary Actor

Trainer, Admin

## Preconditions

* User is authenticated.
* User has Trainer or Admin role.
* Class exists.

## Main Success Scenario

1. Actor requests booking list for a specific class.
2. System verifies permissions.
3. System retrieves list of bookings.
4. System returns:

   * User name
   * User type (Member)
   * Booking timestamp

## Alternative Flows

* **Unauthorized Access:**
  System returns 403 Forbidden.

* **Class Not Found:**
  System returns 404 Not Found.

## Postconditions

* Trainer/Admin can view accurate booking list.

---

# Use Case 5: Register User (`/auth/register`)

## Use Case Name

Create a new account and return access token

## Primary Actor

Guest

## Preconditions

* User is not currently authenticated.

## Main Success Scenarios

1. **Normal User Registration (Member):**
   * **Who:** Any guest/new user.
   * **Request:** Actor provides registration details (name, email, password, etc.) and omits the `token` field.
   * **Result:** System creates the account with the role `"member"` and immediately returns a JWT `access_token`.
2. **Trainer Registration:**
   * **Who:** A user who is allowed to become a trainer.
   * **Request:** Actor provides registration details and includes `"token": "trainer-secret-123"`.
   * **Result:** System creates the account with the role `"trainer"` and returns a JWT `access_token`.
3. **Admin Registration:**
   * **Who:** A user who is allowed to become an admin.
   * **Request:** Actor provides registration details and includes `"token": "admin-secret-456"`.
   * **Result:** System creates the account with the role `"admin"` and returns a JWT `access_token`.

## Alternative Flows

* **Invalid Invite Token:**
  System returns `403 Forbidden` ("Invalid or expired token") if a token is provided but is not in `VALID_TOKENS`.
* **Duplicate Email or Phone:**
  System returns a `409 Conflict` indicating the email or phone is already in use.

## Postconditions

* A new account is created, and the user is instantly logged in (JWT issued).

---

# Use Case 6: Login User (`/auth/login`)

## Use Case Name

Authenticate an existing account

## Primary Actor

Guest, Member, Trainer, Admin

## Preconditions

* User has a registered account.

## Main Success Scenario

1. Actor provides credentials (email and password).
2. System validates credentials.
3. System generates and returns a JWT `access_token`. (The JWT includes role and user_id claims).

## Alternative Flows

* **Missing Email or Password:**
  System returns `400 Bad Request`.
* **Phone Login Attempted:**
  If the request includes a phone field, the system returns `400 Bad Request` ("phone login is not supported; use email").
* **User Not Found:**
  System returns `404 Not Found`.
* **Wrong Password:**
  System returns `400 Bad Request`.

## Postconditions

* Actor receives a JWT token to use as a Bearer token for protected endpoints.

---

# Use Case 7: Validate Invite Token (`/auth/validate-token`)

## Use Case Name

Check whether an invite token is valid

## Primary Actor

Trainer, Admin

## Preconditions

* User has a token to be that need to be validated to confirm their role

## Main Success Scenario

1. Actor requests to confirm an invite token (e.g., `{ "token": "trainer-secret-123" }`).
2. System verifies the token against `VALID_TOKENS`.
3. System returns `200 OK` with `{ "valid": true, "role": "trainer" | "admin" }`.

## Alternative Flows

* **Token is Invalid or Missing:**
  System returns `400 Bad Request` with `{ "valid": false }`.

## Postconditions

* Client application can confidently proceed with or reject the registration flow based on the token validity. *(Note: This does not validate JWTs, only registration invite tokens).*

---

# Authentication and Authorization

## Auth flow (hard-coded invite tokens vs JWT)

### 1: Hard-coded tokens (registration invite tokens)
We have hard-coded **invite tokens** in the backend configuration (`app/apis/auth.py`):
- `"trainer-secret-123"` → registers the user with role `"trainer"`
- `"admin-secret-456"` → registers the user with role `"admin"`

These tokens are only used during **registration** (`POST /auth/register`):
- If the request body includes `"token": "<one of the valid tokens>"`, the backend assigns the matching elevated role.
- If the request body omits `"token"`, the backend defaults the new user’s role to `"member"`.
- These invite tokens are **not** used as authentication for normal API calls. they just decide the role at sign-up time.

### 2: JWT (actual auth token used for protected endpoints)
After a user is registered or logs in, the backend issues a **JWT access token**:
- `POST /auth/register` returns an `access_token` immediately after creating the account.
- `POST /auth/login` returns an `access_token` after validating email + password.

This JWT is what you use to authenticate to protected endpoints. The API checks it from the HTTP header:
- **Header name:** `Authorization`
- **Format:** `Bearer <JWT>`

Role-based access is enforced using the JWT’s `"role"` claim (e.g., calling `verify_jwt_in_request()` and checking `get_jwt()["role"]`).

### 3 Swagger / OpenAPI: how to authorize

In Swagger UI:
1. Click the **Authorize** button (top right).
2. Paste the value in this exact format:
   `Bearer <JWT>`

After that, Swagger will send `Authorization: Bearer <JWT>` on requests, and the backend will treat you as the logged-in user with that role. Failure to include the `Bearer ` prefix will result in authorization failure.
