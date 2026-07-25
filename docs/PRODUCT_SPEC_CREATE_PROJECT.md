# Purpose

The Create Project screen is the primary entry point into the Alpha Research Platform.

Its purpose is to allow users to quickly define a new research project by selecting the business context required for opportunity analysis.

The entire workflow should be simple enough to complete in less than one minute.

This screen collects only the information necessary to start the research process.

No analysis is performed on this screen.

The screen is responsible only for creating a valid research project.

# User Story

## User Story

As an ecommerce entrepreneur,

I want to create a new research project in a few simple steps,

So that I can begin analyzing a product opportunity without unnecessary setup.

## Acceptance Criteria

- The user can create a project in less than one minute.
- Only required information is requested.
- Invalid input is clearly identified.
- The user cannot start research until the project is valid.
- A successful submission creates a new project ready for research.

# Success Criteria

# Screen Layout

The screen is organized into five sections displayed in a single-column layout.

## 1. Page Header

Contains:
- Page Title: Create Project
- Short description explaining the purpose of the screen.

---

## 2. Project Information

Contains:
- Project Name
- Micro Niche

---

## 3. Research Configuration

Contains:
- Marketplace Selection
- Supply Source Selection
- Research Depth

---

## 4. Summary

Displays a read-only summary of the selected configuration before submission.

---

## 5. Actions

Contains:
- Cancel
- Start Research

The Start Research button remains disabled until all required fields are valid.

---

The page should follow a clean, minimal interface prioritizing readability and speed of completion.

# Input Fields

## 1. Project Name

Type:
Text

Required:
Yes

Description:
A human-readable name used to identify the research project.

Constraints:
- Minimum length: 3 characters
- Maximum length: 100 characters
- Must be unique per user
- Leading and trailing whitespace is trimmed

Example:
"Kitchen Storage Research"

---

## 2. Micro Niche

Type:
Text

Required:
Yes

Description:
The specific niche or product category that will be researched.

Constraints:
- Minimum length: 3 characters
- Maximum length: 100 characters

Example:
"Under Sink Organizer"

---

## 3. Marketplaces

Type:
Multi-select

Required:
Yes

Description:
Select one or more marketplaces to analyze.

Initial Options:
- Amazon
- eBay
- Etsy

Minimum Selection:
1

---

## 4. Supply Sources

Type:
Multi-select

Required:
Yes

Description:
Select one or more supplier sources.

Initial Options:
- Alibaba
- Made-in-China

Minimum Selection:
1

---

## 5. Research Depth

Type:
Single Select

Required:
Yes

Default:
Standard

Available Options:
- Quick
- Standard
- Deep

Description:
Determines the depth and duration of the research process.

# Validation Rules

## General Rules

- Validation must occur on both the client and the server.
- Error messages must be clear and actionable.
- Validation errors should appear next to the corresponding field.
- The form must preserve user input after validation errors.
- The Start Research button remains disabled until all required fields are valid.

## Project Name

- Required.
- Between 3 and 100 characters.
- Must be unique for the current user.
- Cannot contain only whitespace.

## Micro Niche

- Required.
- Between 3 and 100 characters.
- Cannot contain only whitespace.

## Marketplaces

- At least one marketplace must be selected.

## Supply Sources

- At least one supply source must be selected.

## Research Depth

- Must be one of:
  - Quick
  - Standard
  - Deep

# User Actions

# API Requirements

# Database Requirements

# Error States

# Empty States

# Future Enhancements
