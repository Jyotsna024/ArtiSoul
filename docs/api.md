# API guide

All routes use `/api/`. Authenticated calls send `Authorization: Bearer <access>`. JWT login accepts `username` and `password`; in the demo accounts the username is the email address. Register accepts username, email, password (10+ characters), first name, last name, and role.

## Learning

`GET /workshops/?search=&category=` lists published workshops. Creator roles (`artisan`, `artist`, `admin`) may create and manage their own listings. `POST /workshops/{id}/enroll/` creates an idempotent learner enrollment, subject to capacity. `GET /enrollments/` lists the current learner's enrollments. `POST /enrollments/{id}/complete/` marks it completed and issues an ArtiSoul certificate. Completion is currently self-attested; add attendance/assessment rules before production.

## Marketplace

`GET /products/?search=&category=` lists products. Creator roles manage listings. `POST /orders/` accepts `{"items":[{"product":1,"quantity":1}]}` and creates a pending order while decrementing reserved stock in a transaction. No payment provider is connected; pending orders are not paid orders.

## Events & tickets

`GET /events/` lists published events. `POST /events/{id}/book/` creates a pending ticket for ArtiSoul events. External events return their organizer URL without claiming a booking. `GET /tickets/` lists the caller's tickets. After a real payment confirmation integration changes ticket status to `confirmed`, `GET /tickets/{id}/qr/` serves its QR image. Creator/admin users can `POST /tickets/verify/` with `{"code":"<ticket UUID>"}` to redeem once. Pending tickets cannot be redeemed.

## Certificates & translation

`GET /certificates/` lists the learner's certificates. `GET /certificates/{id}/pdf/` downloads the ArtiSoul PDF; `GET /certificates/verify/{uuid}/` is public verification. `POST /translation/demo/` accepts `{"text":"...","target_language":"Tamil"}` and explicitly returns a simulated caption with `mode: demo`.

## Remaining platform extensions

Payment webhooks, Azure Speech WebSockets, live video, moderation/community, institutional certificate issuance, richer admin analytics and the full normalized entity set require provider setup and subsequent product phases. The current demo does not present these as operational integrations.
