from flask import Blueprint, request

sut = Blueprint("sut", __name__)

@sut.route("rename", methods=["GET"])
def rename():
    return True
