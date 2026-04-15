![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)
![AI Powered](https://img.shields.io/badge/AI-Powered%20by%20Gemini-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

# 🎩 the-lazy-gorgeous-warden

A sophisticated, AI-powered file system auditor and organizer designed to manage large volumes of personal data with minimal manual effort.

## 🎯 Objective
The primary goal of **the-lazy-gorgeous-warden** is to maintain a pristine and structured environment within high-capacity storage devices (e.g., 2TB HDDs). It acts as an automated "supervisor" that ensures every file adheres to a predefined organizational hierarchy, naming conventions, and security standards.

By leveraging the **Gemini 1.5 Flash** model via API, the Warden doesn't just move files—it understands their context to help you decide where "orphaned" or misplaced data truly belongs.

## 🛠️ Core Features
* **Structure Enforcement:** Automatically audits the directory tree to ensure files are nested within the correct categories (01 to 05).
* **AI-Powered Classification:** Uses Generative AI to analyze and suggest destinations for unknown or disorganized files.
* **Integrity Guard:** Identifies naming violations (spaces, special characters) and normalizes them for better terminal compatibility.
* **Safety First (Dry Run):** Simulates all movements and changes before executing them, providing a detailed audit log.
* **Deduplication:** Uses SHA256 hashing to find and eliminate redundant files across different backup sets.

## 📂 The Warden's Standard Hierarchy
The script enforces a 5-tier structure for personal data:
1.  `01_Personal_Documents/` (IDs, Finance, Health, Contracts)
2.  `02_Digital_Gallery/` (Organized Photos and Videos)
3.  `03_Studies_and_Career/` (Courses, E-books, Certifications)
4.  `04_Entertainment/` (Music, Movies, Software Installers)
5.  `05_Device_Backups/` (Backups from old devices and cloud exports)

## 🚀 Setup
1. Clone this repository.
2. Create a virtual environment: `python3 -m venv venv`.
3. Activate it: `source venv/bin/activate`.
4. Install dependencies: `pip install -r requirements.txt`.
5. Configure your `.env` file based on `.env.example`.

## 🤖 Built with Gemini
This project was architected and developed in collaboration with **Google Gemini**. From the initial directory structure design to the implementation of the modern 2026 `google-genai` SDK, the Warden is a result of an "AI-First" development workflow, focusing on clean code, security, and automation.

---
[Check out the repository here](https://github.com/lucas85cunha/the-lazy-gorgeous-warden)
