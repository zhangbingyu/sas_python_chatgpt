import json
import os
from textwrap import dedent

import openai
from dotenv import load_dotenv
from flask import flash, get_flashed_messages, render_template, url_for
from flask_login import current_user
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

from app import app, db, logger
from forms import OpenAIForm
from models import Transaction, TransactionStatus
from network_plot import generate_network, plot_flowchart

# environment variables
load_dotenv()
openai.organization = os.getenv("ORGANIZATION_ID")
openai.api_key = os.getenv("OPENAI_API_KEY")
# print(openai.Model.list())


system_message = "you are a SAS and Python programming language assistant."
user_message = """You are now a SAS programing and Python expert. Please answer the following questions based on the SAS code enclosed by ``` 
        Question 1: What are the input and output data sets in each block
        Question 2: What are the variables in each data set
        Question 3: Rewrite the codes in Python. 
        Here are some rules:
        1. The variables of the input data set should be inferred from the same output data set in the previous block. 
        2. Please replace macros before answering the questions.
        3. If the input data is a file, use the file name as the data set name. 
        4. If there are more than one input data sets, then there should have the same numbers of the variable lists.
        Please answer the questions in JSON format, with two keys, data_flow and python. 
        The value of python should be formatted string. Make sure that newlines ('\n') are properly handled so that it can be loaded by JSON.
        The value of data_flow should be in JSON format as described below:
        The order of input and output pair should be the same as order of blocks. The JSON should include a list of input and output pair, each pair has 'input' and 'output' two keys. 
        The detailed format is below.
        {{
            "blocks": [
                "input": 
                    {{
                        "names": [list of data sets],
                        "variables": [[list of variables of data set 1], [list of variables of data set 2]]
                    }},
                "output": 
                    {{
                        "names": [list of data sets],
                        "variables": [[list of variables of data set 1], [list of variables of data set 2]]
                    }},
            ]

        }}
         
        Do not include comments. 
        SAS code: 
"""

def get_response(messages, model="gpt-3.5-turbo"):
    """get response from ChatGPT API"""
    response = openai.ChatCompletion.create(
        model=model,
        messages = messages,
        temperature=0,
    )
    return response

def get_price(sas_code):
    """The price of the query based on sas_code"""
    return 1.0

@app.route("/", methods=["GET", "POST"])
# @login_required
def home():
    """main input page"""
    form = OpenAIForm()
    if form.validate_on_submit():
        sas_code = form.sas.data
        if len(sas_code) > 3000:
            flash("The maximum length of code allowed is 3000 in test mode.")
            return render_template("index.html", form=form, messages=get_flashed_messages())
        
        if current_user.is_authenticated:
            price = get_price(sas_code)
            if price > current_user.credit:
                flash("Not enough credit!")
                return render_template("message.html", redirect_url=url_for("home"))
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": dedent(user_message + f"```{sas_code}```")}
            ]
            response, content = handle_response(messages, 0)
            # flow chart
            graph = generate_network(content['data_flow'])
            svg = plot_flowchart(graph)
            lexer = get_lexer_by_name('python')
            formatter = HtmlFormatter(style="github-dark")
            highlighted_code = highlight(content['python'], lexer, formatter)
            # Add the query to the order table
            transaction = Transaction(
                user_id = current_user.id,
                input_token = response['usage']['prompt_tokens'],
                output_token = response['usage']['completion_tokens'],
                status = TransactionStatus.COMPLETION,
                price = price,
            )
            db.session.add(transaction)
            # update credit for the current user
            current_user.credit = current_user.credit - price
            db.session.commit()
            
            # update the order table
            return render_template("index.html", form=form, responses=highlighted_code, chart_output=svg)
        flash("Please Sign in first. Sign up a new account if you have not.")
        return render_template("index.html", form=form, messages=get_flashed_messages())
    return render_template("index.html", form=form)

def handle_response(messages, number_attempt):
    """handle the response from chatgpt and retry one more time if necessary"""
    if number_attempt == 2:
        flash("Something wrong!")
        return render_template("message.html", messages=get_flashed_messages(), redirect_url=url_for("home"))
    try:
        response = get_response(messages)
        logger.info(response.choices[0].message['content'])
    except openai.APIError as e:
        logger.error(f"openai.API error: {e}")
        flash(f"Something wrong: {e}, try it again in a few minutes")
        return render_template("message.html", messages=get_flashed_messages(), redirect_url=url_for("home"))
    try:
        content = json.loads(response['choices'][0].message['content'])
        return response, content
    except json.JSONDecodeError as e:
        logger.error(f"JSON load error: {e}. Trying again with new messages")
        messages.append({"role": "assistant", "content": response['choices'][0].message['content']})
        messages.append({"role": "user", "content": "Please output only JSON format"})
        handle_response(messages, number_attempt + 1)
        # return render_template("message.html", messages=get_flashed_messages(), redirect_url=url_for("home"))