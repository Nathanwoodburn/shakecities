from flask import Flask, make_response, redirect, render_template_string, request, jsonify, render_template, send_from_directory


def render(data):
    return render_template_string(data)