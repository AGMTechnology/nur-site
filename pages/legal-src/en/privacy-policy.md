---
layout: default
title: Privacy Policy - Nūr
permalink: /privacy-policy
---

# Privacy Policy

**Nūr — Qur'an learning for the whole family**
**Last updated: 10 November 2026**

The [French version](fr/politique-de-confidentialite) of this policy is the reference. This English text is a faithful copy of it.

---

## The short version

- **Nūr works without an account.** You can install it, set up your family and
  learn for as long as you like without giving us anything at all.
- **Recordings never leave your phone.** Not to us, not to anyone.
  They are stored in the app's private storage on your device and are never
  uploaded.
- **A child never gets an account.** Only a parent does. Everything about a
  child that Nūr holds was typed in by their parent: a first name and an age.
- **No ads. No advertising identifiers. No behavioural tracking of children.**
  We do not use analytics products that profile people, and we never will for
  children.
- **You can delete everything from inside the app**, in two taps, without
  emailing anybody.

The rest of this document is the detail behind those five sentences.

---

## 1. Who we are

Nūr is made by Ahmed Agoummadane ("we", "us"). For anything in this policy,
including a request to delete your data, write to
**[ahmed.agoummadane@gmail.com](mailto:ahmed.agoummadane@gmail.com)**.

For the purposes of the UK and EU General Data Protection Regulation, we are the
data controller for the information described below.

---

## 2. Nūr works without an account

This matters enough to be its own section. Nūr is offline-first: your family's
progress lives on your phone, and the app is complete without a server.

If you never create an account:

- We hold **nothing** about you or anyone in your household.
- Your family's plan, progress, recordings and settings stay on your device.
- Losing or wiping the phone loses them, because there is no copy anywhere else.

An account exists for exactly one reason: so that a new phone can recover your
family's progress. Creating one is your choice and you can make it at any time,
or never.

---

## 3. What we collect, and only when

### 3.1 Your account — only if you create one

| What | Why | Who holds it |
|---|---|---|
| Your email address | To identify your account and let you sign back in | Supabase |
| Your password | To protect the account. We never see it — it is hashed by our authentication provider before storage | Supabase |

If you sign in with Apple or Google instead, we receive whatever that provider
tells us — normally an email address and an account identifier. If you use
Apple's **Hide My Email**, we receive a relay address and never your real one.
We do not receive your password from either.

### 3.2 Your family's plan — only if you have an account

When you have an account, the app saves one document to our database so it can
be restored on another phone. It contains:

- Each learner's **first name**, **age**, and chosen avatar colour
- Where each learner has reached in the course, and their placement result
- Stars, streaks, hearts, garden items, story progress and league standing
- Your household's chosen intentions, and your reminder time

That is the whole list. It is stored as a single document belonging to your
account, and database rules ensure that no other account can read it.

**What is deliberately excluded from that document:**

- **Recordings.** See below — they never travel.
- Your account identity itself, which is what the document is stored *under*.

### 3.3 Recordings — these never leave your device

When a learner recites, Nūr can record their voice so a parent can listen back.

**Those recordings are never uploaded — not to our servers, not to a third
party, not anywhere.** They are written to the app's private storage on your
phone and stay there. Our database has no table, column or storage bucket that
could hold one, by design and on purpose.

The single exception is you: a parent, behind the parent PIN, can save a
recording to their own phone or send it onward using their phone's share sheet,
to a destination they choose. That is a parent deciding about a voice in their own
household. Nothing is attached automatically, and no learner's name appears
in a shared file unless you type one.

The consequence is real and we accept it: **a lost, reset or replaced phone
loses every recording permanently.** Restoring your account brings back
progress, never audio.

### 3.4 Reminders

The daily practice reminder is scheduled **by your phone, on your phone**. There
is no push server, no device token sent to us, and no record anywhere of whether
you opened it. Turning it on tells us nothing, because nothing is sent.

### 3.5 Crash reports

If the app crashes, we receive a technical report so we can fix it. Those
reports carry the error, the line of code, the app version and the device model.

They are **scrubbed of user identifiers**: no email address, no account
identifier, no learner name, no recording, and nothing a learner typed or said.
Alongside them, the app keeps simple counters on your own device, which you can
see in your parent dashboard and which are not transmitted.

Our crash reporting provider is Sentry.

### 3.6 Subscriptions

If you subscribe, the payment is handled entirely by **Apple's App Store or
Google Play**. We never see your card, your billing address or your full name.
We receive confirmation that a subscription is active, through RevenueCat, which
manages subscription state for us.

Nothing else is ever sold inside the app.

---

## 4. What we do not collect

We think this list is as important as the one above.

- **No advertising.** No ads, no ad networks, no advertising identifiers (IDFA,
  Android Advertising ID), no ad measurement SDKs.
- **No behavioural analytics on children.** No PostHog, no Amplitude, no
  Firebase Analytics, no event stream of what a child did. This was a deliberate
  decision and it is written down in our engineering records, so that a future
  engineer reads it as a decision rather than as a gap.
- **No location data.** Ever, in any form.
- **No contacts, no photo library, no microphone access except while a learner
  is actively recording a recitation they chose to record.**
- **No selling or sharing of personal information**, in the sense those terms
  carry under the California Consumer Privacy Act or any comparable law. We do
  not sell data, and we do not share it for cross-context behavioural
  advertising.
- **No social features, no messaging, no friend-finding, no user-generated
  content between households.** The league shows first names and nothing else:
  no photos, no messages, and no way to find or contact anyone.

---

## 5. Children's privacy

Nūr is built for families and is designed so that a child can use it without a
service ever learning who they are.

**No child ever has an account.** A learner is a profile inside their parent's
household, not a login. Only a parent can create an account, and only a parent
can reach the settings, the recordings and the account controls — those sit
behind a parent PIN.

**A parent provides the only information about a child, and it is minimal:** a
first name and an age. We ask for an age because the app changes how it teaches
and how it speaks for a four-year-old versus an adult, not to profile anyone. We
never ask a child for an email address, a phone number, a photograph, a
surname, or anything that could identify them outside the app.

**Recordings of a child's voice never leave the device** (section 3.3). This is
the strongest privacy commitment in the product and the one we would ask you to
judge us on.

**We do not use persistent identifiers to build a profile of a child or to serve
advertising**, which is the practice the Children's Online Privacy Protection
Act (COPPA) and Article 8 of the GDPR exist to police.

If you believe a child has given us information directly — which the app
provides no way to do — write to us and we will delete it.

---

## 6. Our legal bases (UK/EU GDPR)

| What | Legal basis |
|---|---|
| Holding your account so you can sign back in | Performance of a contract with you |
| Storing your family's plan so it can be restored | Performance of a contract with you |
| Crash reports | Our legitimate interest in a working app, balanced by scrubbing every identifier |
| Subscription status | Performance of a contract with you |

Where a child's information is processed, it is provided by the holder of
parental responsibility, who is our account holder.

---

## 7. Who else touches your data

We use a small number of processors, and we use them for one job each.

| Processor | What they do | What they receive |
|---|---|---|
| **Supabase** | Authentication and the database holding your family's plan | Email address, hashed password, the plan document in section 3.2 |
| **Sentry** | Crash reports | Technical crash data, scrubbed of identifiers |
| **RevenueCat** | Subscription status | An anonymous subscriber identifier and the store's purchase receipt |
| **Apple / Google** | Payment, and sign-in if you choose it | Whatever their own terms describe; we never see payment details |

We do not give your data to anyone else. We would disclose it if compelled by a
valid legal order, and we would tell you unless prohibited from doing so.

---

## 8. Where it is stored, and for how long

Your account and your family's plan are stored on Supabase's infrastructure.
Recordings are stored only on your own device.

We keep your account and its plan **for as long as your account exists**. When
you delete your account, both are deleted (section 9). Crash reports are kept by
Sentry for a limited retention window and then discarded.

---

## 9. Your rights, and how to use them

**Deletion, without asking us.** Nūr has account deletion built in. Open the
parent area, go to your account, and choose to delete it. This removes your
account and your family's plan from our database, and wipes everything on the
device including recordings. It cannot be undone. If your household never made
an account, the same control still wipes the device.

Two things worth knowing before you use it:

- **If you are signed out but your family's plan was once saved to an account,
  we will ask you to sign in first.** We could empty your phone without it, but
  then our copy would still be there and we would have told you otherwise.
- **Deleting your account does not cancel a subscription.** Apple and Google
  bill you, not us, so a subscription has to be cancelled in your Apple or
  Google account settings. We cannot do it for you and deleting your account
  will not do it either.

You also have the right to **access** the information we hold, to have it
**corrected**, to have it **exported** in a portable form, to **object** to
processing based on legitimate interests, and to **complain** to your data
protection authority — in the EU, your national authority; in the UK, the
Information Commissioner's Office.

To exercise any of these, write to
**[ahmed.agoummadane@gmail.com](mailto:ahmed.agoummadane@gmail.com)**. We answer
within 30 days.

---

## 10. Security

Passwords are hashed by our authentication provider and never stored or
transmitted in a readable form by us. Every request between the app and our
database travels over TLS. Access to your family's plan is enforced at the
database itself by row-level security rules, so one account cannot read
another's — this is not left to the app to get right.

No system is perfect, and we will not claim otherwise. If we ever discover a
breach affecting your data, we will tell you and the relevant authority within
the timeframes the law requires.

---

## 11. International transfers

Our processors may store or process data outside your country, including in the
United States. Where that involves personal data from the UK or EU, those
transfers rely on the European Commission's Standard Contractual Clauses or an
adequacy decision, as set out in each processor's own terms.

---

## 12. Changes to this policy

If we change this policy we will update the date at the top. If a change
materially affects what we collect or who receives it, we will tell you in the
app before it takes effect.

---

## 13. Contact

**Email:** [ahmed.agoummadane@gmail.com](mailto:ahmed.agoummadane@gmail.com)

---

[Terms of Service](terms-of-service) · [Home](./)
