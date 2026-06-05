---
title: OAuth 2.0 Flows
aliases: [OAuth, authorization, access tokens]
tags: [security]
tier: public
status: verified
created: 2026-02-15
---

# OAuth 2.0 Flows

OAuth 2.0 is an authorization framework that enables third-party applications to access resources on behalf of a user without exposing credentials. It defines several grant types for different use cases.

## Authorization Code Flow

The most secure flow for server-side applications. The client redirects the user to the authorization server, which returns an authorization code. The client exchanges this code for access and refresh tokens via a back-channel request.

## PKCE Extension

Proof Key for Code Exchange adds security for public clients (mobile apps, SPAs) that cannot securely store a client secret. The client generates a random code verifier and sends its hash (code challenge) with the authorization request.

## Token Management

Access tokens are short-lived (minutes to hours). Refresh tokens are long-lived and used to obtain new access tokens without re-authorization. Token revocation endpoints allow immediate invalidation. JWT-formatted tokens enable stateless validation.
