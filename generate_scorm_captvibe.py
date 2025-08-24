import os
import requests
import markdown
import base64
import re
import random

# ---------- CONFIG ----------
GITHUB_USER = "pacobaco"       # your GitHub username
REPO_NAME = "captvibe"         # renamed repo/project
BRANCH = "main"
OUTPUT_DIR = "captvibe-scorm"  # renamed output folder
ASSETS_DIR = os.path.join(OUTPUT_DIR, "assets", "images")
SCORM_JS = "scormdriver.js"

# ---------- HELPER FUNCTIONS ----------
def fetch_repo_tree():
    url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/git/trees/{BRANCH}?recursive=1"
    resp = requests.get(url)
    resp.raise_for_status()
    tree = resp.json()['tree']
    projects = {}
    for item in tree:
        if item['path'].endswith("README.md"):
            project_name = item['path'].split('/')[0]
            projects[project_name] = item['url']
    return projects, tree

def fetch_readme_html(url):
    resp = requests.get(url)
    resp.raise_for_status()
    content = resp.json()['content']
    md_text = base64.b64decode(content).decode('utf-8')
    return markdown.markdown(md_text), md_text

def fetch_project_images(project_name, tree):
    img_dir = os.path.join(ASSETS_DIR, project_name)
    os.makedirs(img_dir, exist_ok=True)
    images_html = ""
    for item in tree:
        if item['path'].startswith(f"{project_name}/") and item['path'].lower().endswith(('.png','.jpg','.jpeg','.gif')):
            raw_url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{BRANCH}/{item['path']}"
            filename = os.path.basename(item['path'])
            r = requests.get(raw_url)
            with open(os.path.join(img_dir, filename), 'wb') as f:
                f.write(r.content)
            images_html += f'<img src="assets/images/{project_name}/{filename}" alt="{filename}" width="300">\n'
    return images_html

def extract_headings(md_text):
    headings = re.findall(r'^(?:##|###)\s+(.*)', md_text, re.MULTILINE)
    return headings

def extract_functions(tree, project_name):
    funcs = []
    for item in tree:
        if item['path'].startswith(f"{project_name}/") and item['path'].endswith(('.py','.js','.html')):
            raw_url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{BRANCH}/{item['path']}"
            r = requests.get(raw_url).text
            funcs += re.findall(r'def\s+(\w+)|function\s+(\w+)', r)
    funcs = [f[0] or f[1] for f in funcs if f[0] or f[1]]
    return funcs

def generate_quiz_items(headings, funcs, max_questions=3):
    items = []
    pool = headings + funcs
    if not pool: return []
    for topic in headings[:max_questions]:
        correct = topic
        distractors = random.sample([x for x in pool if x != topic], min(2, len(pool)-1)) if len(pool) > 1 else ['Option1','Option2']
        options = [correct] + distractors
        random.shuffle(options)
        items.append({'question': f"What is the purpose of '{topic}'?", 'options': options, 'answer': correct})
    return items

def create_project_html(project_name, html_content, images_html, quiz_items, index):
    filename = f"project{index+1}.html"
    filepath = os.path.join(OUTPUT_DIR, filename)

    # Build quiz HTML and JS for per-question scoring
    quiz_html = f"<h2>Quiz: {project_name}</h2>\n<form id='quizForm{index}'>\n"
    checks_js = ""
    num_questions = len(quiz_items)
    for i, q in enumerate(quiz_items):
        quiz_html += f"<p>{q['question']}</p>\n"
        for opt in q['options']:
            quiz_html += f"<input type='radio' name='q{i}' value='{opt}'> {opt}<br>\n"
        checks_js += f"""
        var val{i} = document.forms['quizForm{index}'].q{i}.value;
        if(val{i} === "{q['answer']}"){{ score += 100/num_questions; }}
        """
    quiz_html += f"<button type='button' onclick='submitQuiz({index})'>Submit Quiz</button>\n</form>"

    js_quiz = f"""
    <script>
    function submitQuiz(idx){{
        var score=0;
        var totalQuestions = {num_questions};
        var pointsPerQuestion = 100 / totalQuestions;
        {checks_js}
        completeCourse(score);
        alert("Quiz completed! Score: "+score.toFixed(2));
    }}
    </script>
    """

    page = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <title>{project_name}</title>
    <script src="{SCORM_JS}"></script>
    </head>
    <body>
    <h1>{project_name}</h1>
    {html_content}
    <h2>Screenshots</h2>
    {images_html}
    {quiz_html}
    {js_quiz}
    <p><a href="index.html">Back to Main Menu</a></p>
    </body>
    </html>
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(page)
    return filename

def create_index_html(project_files, project_names):
    filepath = os.path.join(OUTPUT_DIR, "index.html")
    links = "\n".join([f'<li><a href="{f}">{n}</a></li>' for f,n in zip(project_files, project_names)])
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <title>CaptVibe GitHub Course</title>
    <script src="{SCORM_JS}"></script>
    </head>
    <body onload="initCourse()">
    <h1>CaptVibe GitHub Projects</h1>
    <ul>
    {links}
    </ul>
    </body>
    </html>
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

def create_scorm_manifest(project_files, project_names):
    resources = ""
    items = ""
    for i,(f,n) in enumerate(zip(project_files, project_names)):
        res_id = f"RES{i+1}"
        item_id = f"ITEM{i+1}"
        resources += f"""
        <resource identifier="{res_id}" type="webcontent" adlcp:scormtype="sco" href="{f}">
          <file href="{f}"/>
          <file href="{SCORM_JS}"/>
        </resource>"""
        items += f"""
      <item identifier="{item_id}" identifierref="{res_id}">
        <title>{n}</title>
      </item>"""
    manifest = f"""<manifest identifier="captvibe-course" version="1.2"
    xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2"
    xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.imsproject.org/xsd/imscp_rootv1p1p2
                        imscp_rootv1p1p2.xsd
                        http://www.adlnet.org/xsd/adlcp_rootv1p2
                        adlcp_rootv1p2.xsd">
  <organizations default="ORG1">
    <organization identifier="ORG1">
      <title>CaptVibe GitHub Course</title>{items}
    </organization>
  </organizations>
  <resources>{resources}
  </resources>
</manifest>"""
    with open(os.path.join(OUTPUT_DIR,"imsmanifest.xml"), 'w', encoding='utf-8') as f:
        f.write(manifest)

def create_scorm_js():
    js_content = """var pipwerks = pipwerks || {};
pipwerks.SCORM = pipwerks.SCORM || {};
function initCourse() {
    if(typeof pipwerks.SCORM.init === "function") { pipwerks.SCORM.init(); }
}
function completeCourse(score){
    if(typeof pipwerks.SCORM.set === "function"){
        if(score !== undefined){ pipwerks.SCORM.set("cmi.core.score.raw", score); }
        pipwerks.SCORM.set("cmi.core.lesson_status","completed");
        pipwerks.SCORM.save();
        pipwerks.SCORM.quit();
    }
}
"""
    with open(os.path.join(OUTPUT_DIR, SCORM_JS),'w', encoding='utf-8') as f:
        f.write(js_content)

# ---------- MAIN ----------
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

print("Fetching projects from GitHub...")
projects, repo_tree = fetch_repo_tree()
project_files = []
project_names = []

for i,(proj,url) in enumerate(projects.items()):
    print(f"Processing {proj}...")
    html_content, md_text = fetch_readme_html(url)
    images_html = fetch_project_images(proj, repo_tree)
    headings = extract_headings(md_text)
    funcs = extract_functions(repo_tree, proj)
    quiz_items = generate_quiz_items(headings, funcs)
    filename = create_project_html(proj, html_content, images_html, quiz_items, i)
    project_files.append(filename)
    project_names.append(proj)

create_index_html(project_files, project_names)
create_scorm_manifest(project_files, project_names)
create_scorm_js()

print(f"CaptVibe SCORM package generated in {OUTPUT_DIR}/")
