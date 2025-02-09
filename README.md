# Smart-Stock-Rocket
Smart stock rocket is an all-around financial planning and advising AI designed to help users manage their money smartly. This app focuses on providing spending insights, financial planning tools, and recommendations to improve savings and long-term financial success. The primary focus is on improving user budgeting, savings, and financial literacy.

## Getting Started with Development
1. Install Python
    - Note: I (Calum) am using Python 3.13.2.
2. Install Miniconda
3. Import environment from environment.yml using conda and activate environment

```console
conda env create -f environment.yml
conda activate smart-stock-rocket
```

4. Start Flask web app on local host

```console
flask --app app --debug run
```

5. You're ready to start making changes! As you make changes, save the files and reload the page to see your applied changes.

## Project Structure
> Note that this is subject to change, this describes the initial project structure

```
Smart-Stock-Rocket
├─── app
|    ├─── home
|    │    ├─── routes.py
|    │    └─── __init__.py
|    ├─── static
|    │    └─── styles.css
|    ├─── templates
|    |    ├─── base.html
|    |    └─── index.html
|    └─── __init__.py
├─── config.py
├─── environment.yml
└─── README.md
```

### Adding a Web Page
1. Add a folder to `app/templates`
    - This folder will store the `index.html` for the new web page
2. Add a folder to `app` for the new web page
    - This folder will contain an `__init__.py` which contains the blueprint for the new web page and `routes.py` which contains any routes for your web page
3. Add the blueprint to `app/__init__.py` in the `create_app()` function

> Note that `templates/base.html` is the base template that is extended in other templates. This contains the reused boilerplate, such as the navigation bar for navigating to different parts of the application.
