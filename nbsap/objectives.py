import schema
import flask
import sugar
from database import mongo

objectives = flask.Blueprint("objectives", __name__)

def initialize_app(app):
    app.register_blueprint(objectives)

@objectives.route("/objectives/<int:objective_id>/<int:subobj_id>")
@sugar.templated("objectives/subobj_view.html")
def view_subobj(objective_id, subobj_id):

    objective = mongo.db.objectives.find_one_or_404({"id": objective_id})

    try:
        subobj = [s for s in objective['subobjs'] if s['id'] == subobj_id][0]
    except IndexError:
        flask.abort(404)

    objective_related_actions = mongo.db.actions.find_one({"id": objective_id})

    if objective_related_actions:
        related_action = [a for a in objective_related_actions['actions']
                                if int(a['title']['en'].split('.')[1]) == subobj_id][0]

    return {
                "objective_id": objective_id,
                "subobj": subobj,
                "action": related_action
           }

@objectives.route("/objectives/<int:objective_id>")
@sugar.templated("objectives/view.html")
def view(objective_id):

    objective = mongo.db.objectives.find_one_or_404({'id': objective_id})
    actions = mongo.db.actions.find_one({'id': objective_id})

    if actions:
        related_actions = actions.get('actions', None)

    return {
                "objective": objective,
                "actions": related_actions
           }

@objectives.route("/objectives")
@sugar.templated("objectives/objectives_listing.html")
def list_objectives():

    objectives = mongo.db.objectives.find()

    return {
            "objectives": objectives,
           }

@objectives.route("/objectives/data")
def objective_data():
    try:
        id_code = flask.request.args.getlist('id_code')[0]
    except IndexError:
        return flask.jsonify({'result': ''})

    objective_id = int(id_code.split('.')[0])
    subobjective_id = int(id_code.split('.')[1])

    objective = mongo.db.objectives.find_one_or_404({"id": objective_id})
    subobjective = [s for s in objective['subobjs'] if s['id'] == subobjective_id][0]

    result = {'result': subobjective['title']['en']}
    return flask.jsonify(result)

@objectives.route("/objective/<int:objective_id>/edit", methods=["GET", "POST"])
@sugar.templated("objectives/edit.html")
def edit(objective_id):

    objective = mongo.db.objectives.find_one_or_404({'id': objective_id})
    objective_schema = schema.Objective(objective)

    # default display language is English
    try:
        selected_language = flask.request.args.getlist('lang')[0]
    except IndexError:
        selected_language = u'en'

    app = flask.current_app

    if flask.request.method == "POST":
        data = flask.request.form.to_dict()

        selected_language = data['language']

        objective_schema['title'][selected_language].set(data['title-' + selected_language])
        objective_schema['body'][selected_language].set(data['body-' + selected_language])

        if objective_schema.validate():
            objective['title'][selected_language] = data['title-' + selected_language]
            objective['body'][selected_language] = data['body-' + selected_language]

            flask.flash("Saved changes.", "success")
            mongo.db.objectives.save(objective)

    return {
                "language": selected_language,
                "objective": objective,
                "schema": objective_schema
           }
