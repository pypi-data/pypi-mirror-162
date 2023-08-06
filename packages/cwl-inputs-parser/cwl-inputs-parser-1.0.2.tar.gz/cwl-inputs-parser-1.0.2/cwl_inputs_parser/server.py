#!/usr/bin/env python3
# coding: utf-8
import tempfile
from pathlib import Path
from traceback import format_exc
from typing import Tuple

import yaml
from cwl_utils.parser import load_document_by_string
from flask import Blueprint, Flask, Response, jsonify, request

from cwl_inputs_parser.utils import (Inputs, cwl_make_template,
                                     wf_location_to_inputs)

app_bp = Blueprint("cwl-inputs-parser", __name__)


@app_bp.route("/health", methods=["GET"])
def health() -> Tuple[Response, int]:
    """
    Health check.
    """
    res = jsonify({"message": "OK"})
    res.headers["Access-Control-Allow-Origin"] = "*"
    return res, 200


@app_bp.route("/", methods=["GET", "POST"])
def parse() -> Tuple[Response, int]:
    """
    Parse the inputs of a workflow.
    """
    req_data = yaml.safe_load(request.get_data().decode("utf-8"))
    wf_location = req_data.get("wf_location", None)
    wf_content = req_data.get("wf_content", None)
    if wf_location is None and wf_content is None:
        return jsonify({"message": "Missing arguments"}), 400
    if wf_location is not None:
        inputs = wf_location_to_inputs(wf_location.strip())
    elif wf_content is not None:
        wf_obj = load_document_by_string(wf_content, uri=Path.cwd().as_uri())  # noqa: E501
        inputs = Inputs(wf_obj)
    res = jsonify(inputs.as_dict())
    res.headers["Access-Control-Allow-Origin"] = "*"
    return res, 200


@app_bp.route("/make-template", methods=["GET", "POST"])
def cwl_make_template_route() -> Tuple[Response, int]:
    """
    Create a template for a CWL file.
    """
    req_data = yaml.safe_load(request.get_data().decode("utf-8"))
    wf_location = req_data.get("wf_location", None)
    wf_content = req_data.get("wf_content", None)
    if wf_location is None and wf_content is None:
        return jsonify({"message": "Missing arguments"}), 400
    if wf_location is not None:
        template_data = cwl_make_template(wf_location.strip())
    elif wf_content is not None:
        with tempfile.NamedTemporaryFile(suffix=".cwl") as temp_file:
            temp_file.write(wf_content.encode("utf-8"))
            temp_file.flush()
            template_data = cwl_make_template(temp_file.name)
    res = jsonify(template_data)
    res.headers["Access-Control-Allow-Origin"] = "*"
    return res, 200


def create_app() -> Flask:
    """
    Create the Flask app.
    """
    app = Flask(__name__)
    app.register_blueprint(app_bp)
    return app


def fix_errorhandler(app: Flask) -> Flask:
    @app.errorhandler(Exception)
    def error_handler_exception(exception: Exception) -> Tuple[Response, int]:
        return jsonify({"message": f"The server encountered an internal error:\n{format_exc()}"}), 500  # noqa: E501

    return app
