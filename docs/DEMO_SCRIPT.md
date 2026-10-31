# Educentriks Cognify — 3-Minute Hackathon Demo Script

> **Product:** Educentriks Cognify  
> **Parent Organization:** Educentriks (Education. Evolved.)  
> **Target Certification:** Microsoft Certified: Azure AI Apps and Agents Developer Associate (AI-103)  
> **Problem Statement:** PS02 — Adaptive Exam-Prep Tutor with Evidence-Based Learner Model

---

## Demo Overview for Judges

| Segment | Timing | Key Capability Demonstrated |
|---|---|---|
| **1. The Problem & Introduction** | 0:00 – 0:30 | Why static certification prep fails; introducing Educentriks Cognify |
| **2. Voice-First Onboarding & Diagnostic** | 0:30 – 1:15 | Natural voice capture, profile grounding, targeted diagnostic questioning |
| **3. Rubric Evaluation & Misconception Detection** | 1:15 – 2:00 | 4-part weighted scoring, reasoning evaluation, state transition |
| **4. Concept Graph & Adaptive Recommendation** | 2:00 – 2:30 | Prerequisite graph, stepped-down difficulty, spaced repetition scheduling |
| **5. Cohort Analytics & Conclusion** | 2:30 – 3:00 | Privacy-preserving institutional gap analysis, production readiness |

---

## Step-by-Step Walkthrough

### 1. Hook & Introduction (0:00 – 0:30)
- **Say:** *"Most AI certification prep treats every student like a blank slate—forcing experienced engineers to slog through basics while leaving career switchers lost without prerequisites. This is **Educentriks Cognify**, a voice-first adaptive learning coach built for the Microsoft AI-103 certification."*
- **Action:** Show the clean Educentriks branded interface. Point out the learner switcher in the sidebar (Alex Rivera: Career-Switcher vs. Sarah Chen: Solutions Architect).

---

### 2. Voice-First Onboarding & Diagnostic (0:30 – 1:15)
- **Say:** *"Cognify meets learners where they are. Alex is a developer transitioning to AI engineering. Let's ask Cognify to test our understanding of Agent Tool Calling."*
- **Action:** Click **Speak Answer** (or type) and prompt:
  > *"Can you give me a diagnostic question on Agent Tool Calling so I can test my knowledge?"*
- **Tutor Response:** Cognify generates an original scenario question on tool calling (not a copyrighted exam question).

---

### 3. Reasoning Evaluation & Misconception Detection (1:15 – 2:00)
- **Say:** *"Now, watch how Cognify evaluates not just the answer, but the learner's underlying conceptual reasoning."*
- **Action:** Click **Speak Answer** and provide a response with a common misconception:
  > *"Tool calling allows an LLM to run external tasks by executing the Python code directly inside its neural network weights."*
- **Tutor Evaluation:**
  - Evaluates across the 4-part rubric: Technical Correctness (40%), Reasoning (25%), Use Case (20%), Security (15%).
  - Identifies the misconception: *LLMs output structured execution schemas; the client runtime executes the code.*
  - Calculates the composite score (e.g. 62.5/100).
  - Updates mastery status to `developing` or `needs_revision`.

---

### 4. Prerequisite Knowledge Graph & Adaptation (2:00 – 2:30)
- **Say:** *"Instead of blindly giving another hard question, Cognify checks our prerequisite concept graph."*
- **Action:** Click on **Curriculum & Mastery Graph (Tab 2)**:
  - Point to **Agent Tool Calling**—now marked with updated status and evidence confidence.
  - Show the prerequisite chain: *LLM Fundamentals → Tool Calling → Agent State & Memory*.
  - Show the **Spaced Repetition Schedule**: a review has been automatically scheduled for tomorrow to reinforce this weak area.
- **Action:** Point to the sidebar: The **Next Recommended Activity** card has adapted dynamically to prescribe foundational reinforcement.

---

### 5. Institutional / Cohort Analytics (2:30 – 3:00)
- **Say:** *"Finally, for instructors and educational institutions, Cognify provides a privacy-preserving cohort dashboard."*
- **Action:** Switch to **Cohort Analytics (Tab 3)**:
  - Show the **Class Concept Gap Distribution** showing aggregate counts of students needing revision vs proficient.
  - Highlight the **Recurring Misconceptions** card: instructors instantly see that multiple students misunderstand runtime tool execution.
  - Note: *Zero student private responses or chat logs are ever exposed.*
- **Wrap-up:** *"Educentriks Cognify turns static certification study into an intelligent, evidence-grounded coaching experience. Education. Evolved. Thank you!"*

---

## Fallback & Demo Safety Precautions

1. **Microphone denied or noisy environment?**
   - Use the typed chat input directly below the mic button. Both execute the identical agent pipeline.
2. **Database reset before demo?**
   - Run `python -m api.seed_demo_data` to restore clean benchmark states in 2 seconds.
3. **Session reset?**
   - Click **Clear Conversation** in the sidebar to reset the active chat history.

