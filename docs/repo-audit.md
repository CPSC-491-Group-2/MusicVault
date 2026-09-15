# Music Vault Existing Repository Audit

## Overview

The existing Music Vault repository was reviewed to determine what parts of the previous prototype were implemented, what appears incomplete or broken, and what may be reusable for the current CPSC 491 project.

The old repository contains three major areas:

- `client` for the frontend
- `musicvault_backend` for a Django backend
- `server` for a separate Node/Express backend

This creates overlapping backend responsibilities and appears to be one of the main sources of integration confusion in the previous prototype.

## Frontend

The `client` folder is a React + TypeScript application created with Vite.

The project contains the standard Vite structure, including:

- `src`
- `public`
- `package.json`
- TypeScript configuration files
- ESLint configuration
- Vite configuration

The frontend README is still the default React/Vite template and does not contain Music Vault-specific setup documentation.

### Frontend Implementation Status

`App.tsx` is extremely minimal and only imports and renders the `Home` component.

`Home.tsx` is also mostly a placeholder. It only displays one of two headings depending on whether a hard-coded `name` string is empty.

No working frontend implementation was found for:

- user registration/login forms
- Spotify account linking
- API calls
- recommendation results
- charts
- CSV download
- routing
- state management
- user preferences

### Frontend Conclusion

The frontend framework was initialized, but very little Music Vault-specific functionality was implemented.

## Django Backend

The `musicvault_backend` directory contains a standard Django project structure with:

- `manage.py`
- Django project configuration files
- a `users` app

The Django project appears to have been created using Django 5.2.1.

### Django Configuration

The Django `settings.py` file is mostly still the default configuration.

Important findings:

- The database is configured as SQLite, not MongoDB.
- The `users` app is not registered in `INSTALLED_APPS`.
- Django REST Framework is not registered in `INSTALLED_APPS`.
- No CORS configuration was found.
- No Spotify-related environment settings were found.
- `DEBUG` is enabled.
- `ALLOWED_HOSTS` is empty.
- A Django secret key is hard-coded directly in the repository.

This conflicts with the root README, which describes MongoDB, Spotify integration, and secure configuration.

### Django User App

The `users` app contains:

- `models.py`
- `serializers.py`
- `views.py`
- `urls.py`
- `tests.py`

`models.py` is still the default empty Django file and contains no user-specific models.

`serializers.py` contains a real `RegisterSerializer` using Django's built-in User model. It accepts username, email, and password and uses Django password validation.

`views.py` contains a `RegisterView` based on Django REST Framework's `CreateAPIView`.

`users/urls.py` defines a `register/` route for the registration view.

However, the main Django project `urls.py` only exposes the default admin route and does not include `users.urls`. Therefore, the registration route is not reachable from the main application.

`tests.py` is still empty and contains no automated tests.

### Django Conclusion

The Django backend contains some partially implemented registration code, but the project is not fully wired together and would require significant configuration before it could run correctly.

## Node/Express Backend

The `server` directory contains a separate Node/Express backend with:

- `controllers`
- `middleware`
- `models`
- `routes`
- `app.js`
- `package.json`
- `node_modules`

This confirms that the old prototype used both Django and Express at the same time.

The committed `node_modules` directory is a repository hygiene issue and should normally be excluded through `.gitignore`.

### Express Application Setup

`app.js` contains real Express setup and includes:

- Express
- CORS
- `express-session`
- dotenv
- Passport
- JSON parsing
- auth routes
- intended Spotify routes

The application mounts:

- `/api/auth/`
- `/api/spotify/`

and starts on port 5000 by default.

However, `app.js` attempts to import `./routes/spotify`, but no `spotify.js` file exists in the routes directory.

This would likely cause the server to fail during startup.

## Authentication

The Express auth route and controller contain partially implemented local registration and login functionality.

### authController.js

The registration flow attempts to:

- check whether an email already exists
- hash the user's password with bcrypt
- create a user
- generate a JWT

The login flow attempts to:

- find a user by email
- compare passwords
- generate a JWT

However, several bugs were found.

In the registration function:

- `user_id` is used when creating the JWT but is never defined.

In the login function:

- the database result is stored in `userExists`
- the code later refers to `user`, which is never defined
- `user.password` is therefore invalid
- `user_id` is again used without being defined

Because of these issues, both local registration and login appear broken as committed.

## Spotify Integration

Spotify integration code exists in multiple places, which creates duplication.

`server/routes/auth.js` contains Spotify OAuth configuration using `passport-spotify`.

`server/middleware/passport.js` also configures a Spotify strategy.

The Passport middleware:

- reads Spotify client credentials from environment variables
- handles Spotify callbacks
- looks up users by Spotify ID
- creates Spotify-linked users
- updates access and refresh tokens
- serializes and deserializes users

However, Spotify configuration is duplicated between `auth.js` and `passport.js`.

`auth.js` also redirects successful Spotify login to:

`http://localhost:3000/dashboard`

while the frontend uses Vite, which commonly uses port 5173 unless configured otherwise.

This suggests another likely frontend/backend integration mismatch.

## MongoDB / Database

The Express backend contains a real Mongoose `User` model.

The schema contains:

- email
- password
- Spotify ID
- Spotify access token
- Spotify refresh token
- favorites
- timestamps

This supports the README's claim that MongoDB was intended for the Express side.

However, no application-level MongoDB connection setup was found.

A repository search for:

`mongoose.connect`

returned no results.

A search for:

`MONGO_URI`

did not reveal any application source code using a MongoDB connection string.

As a result, the Mongoose models and authentication code do not appear to have a configured database connection in the committed source.

## Package Configuration

The Express `package.json` includes dependencies for:

- Express
- Mongoose
- Passport
- Passport Spotify
- CORS
- dotenv
- express-session
- Axios

However, several issues were found:

- There is no start script.
- The package `main` field points to `index.js`, but the visible entry file is `app.js`.
- `bcryptjs` is used in the auth controller but is not listed in dependencies.
- `jsonwebtoken` is used in the auth controller but is not listed in dependencies.
- No automated test framework or test suite is configured.

## Repository Hygiene Issues

Several repository hygiene problems were found:

- `node_modules` is committed to the repository.
- Python `__pycache__` files are committed.
- A Django secret key is hard-coded in source code.
- The README contains setup inconsistencies.
- The README says the database is MongoDB, but Django is configured for SQLite.
- The README migration step incorrectly uses `python manage.py runserver`.
- The README environment example contains `EBUG=True`, which appears to be a typo for `DEBUG=True`.

## Reusable Components

Some parts of the old repository may still be useful as references:

- the React/Vite project setup
- the Django registration serializer/view pattern
- the Express server structure
- the Mongoose User schema
- the Passport Spotify strategy
- some of the authentication flow concepts

These should be treated as reference implementations rather than production-ready code.

## Components That Likely Need to Be Rebuilt or Reworked

The following areas appear incomplete or broken enough that rebuilding or heavily refactoring them is likely more practical:

- frontend feature implementation
- backend architecture
- database connectivity
- local authentication
- Spotify route organization
- frontend/backend integration
- automated tests
- deployment configuration
- environment and secret management

## Final Assessment

The previous Music Vault repository contains useful starter code and partial implementations, but it is not a complete or stable application.

The largest issue is that the project mixes React, Django, Express, SQLite, MongoDB, Passport, and Spotify logic without a fully integrated architecture.

The current CPSC 491 team should use the old repository mainly as a reference for previous ideas and partial implementations rather than assuming it can be continued without major restructuring.