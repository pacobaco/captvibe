# CaptVibe

**CaptVibe** is an automated SCORM course generator for GitHub repositories. It converts your project documentation into interactive e-learning modules with images, auto-generated quizzes, and LMS score tracking.  

---

## Features

- Converts **README.md** files into HTML content for SCORM courses.  
- Automatically includes project **images/screenshots**.  
- Generates **multiple-choice quizzes** from README headings and project functions.  
- Tracks **per-question scores** in SCORM-compliant LMS systems.  
- Produces a fully packaged SCORM course with:
  - `index.html`
  - `projectX.html`
  - `imsmanifest.xml`
  - `scormdriver.js`
- Supports **partial scoring** for granular assessment.  

---

## Installation

1. Clone the repository:  
```bash
git clone https://github.com/pacobaco/captvibe.git
cd captvibe
```
2.	Install required Python packages:
```bash
pip install requests markdown
```
3.	Run the generator script:
```bash
python generate_scorm_captvibe.py
```
4.	The SCORM package will be generated in the captvibe-scorm/ folder.

⸻

Usage
	•	Upload the captvibe-scorm/ folder to any SCORM-compliant LMS.
	•	Each GitHub project becomes a separate SCO (module).
	•	Learners interact with auto-generated quizzes; scores and completion are tracked.
	•	The index.html provides a main menu for navigation.

⸻

## Folder Structure

captvibe/
├── generate_scorm_captvibe.py
├── scormdriver.js
├── captvibe-scorm/
│   ├── index.html
│   ├── project1.html
│   ├── project2.html
│   ├── imsmanifest.xml
│   └── assets/images/...

## Customization
	•	Adjust max_questions per project in the script.
	•	Modify quiz generation logic to include more function names or headings.
	•	Images are automatically pulled from project directories.

⸻

## License

MIT License – free to use and modify.

---

I can also **package the README.md and the Python script into a ready-to-download ZIP file** so you can instantly deploy CaptVibe.  

Do you want me to create the **downloadable ZIP** for you next?
