import flask
from flaskext.babel import gettext as _

import schema
import sugar
from database import mongo
from auth import auth_required


targets = flask.Blueprint("targets", __name__)


def initialize_app(app):
    app.register_blueprint(targets)


@targets.route("/admin/targets")
@auth_required
@sugar.templated("targets/targets_listing.html")
def list_targets():
    aichi_targets = mongo.db.targets.find()

    return {
        "targets": aichi_targets
    }


@targets.route("/targets/data")
def target_data():
    target_ids = flask.request.args.getlist('other_targets', None)
    aichi_targets = []

    for target_id in target_ids:
        aichi_target = mongo.db.targets.find_one_or_404({"id": target_id})
        data = {
            'title': sugar.translate(aichi_target['title']),
            'description': sugar.translate(aichi_target['description'])
        }
        aichi_targets.append(data)

    result = {'result': aichi_targets}
    return flask.jsonify(result)


@targets.route("/admin/targets/<string:target_id>/edit",
               methods=["GET", "POST"])
@auth_required
@sugar.templated("targets/edit.html")
def edit(target_id):

    target = mongo.db.targets.find_one_or_404({'id': target_id})
    target_schema = schema.Target(target)

    # default display language is English
    try:
        lang = flask.request.args.getlist('lang')[0]
    except IndexError:
        lang = u'en'

    if flask.request.method == "POST":
        data = flask.request.form.to_dict()

        lang = data['language']

        target_schema['title'][lang].set(data['title-' + lang])
        target_schema['description'][lang].set(data['body-' + lang])

        if target_schema.validate():
            target['title'][lang] = data['title-' + lang]
            target['description'][lang] = data['body-' + lang]

            flask.flash(_("Saved changes."), "success")
            mongo.db.targets.save(target)

    return {
        "language": lang,
        "target": target,
        "schema": target_schema
    }
