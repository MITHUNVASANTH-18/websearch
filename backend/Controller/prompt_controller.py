from schema.prompt_schema import prompt
from flask import request,jsonify
import json
class PromptClass():
    def postPrompt():
        try:
            data = request.json
            if(data):
                promptdata = prompt(**data)
                promptdata.save()
                return jsonify({"prompt created successfully":str(promptdata.id)}),200
            else:
                return jsonify({"warning":"no data found to store"}),303
        except Exception as e:
            return jsonify({"Error":str(e)}),500
    
    def getPromptById():
        try:
            id =request.args.get('id')
            promptdata = prompt.objects(id=id).first()
            if promptdata:
                promptdata = promptdata.to_json()
                promptdata = json.loads(promptdata)
                return jsonify(promptdata),200
            else:
                return jsonify({"warning": "No prompt found with the given ID"}), 404
        except Exception as e:
            return jsonify({"Error": str(e)}), 500
        
    def updatePrompt():
        try:
            id = request.args.get('id') 
            promptdata = prompt.objects(id=id).first()  

            if not promptdata:
                return jsonify({"message": "No prompt found with the given ID"}), 404

            data = request.json  

            if not data:
                return jsonify({"message": "No input data found to update"}), 400

            promptdata.update(**data) 
            updated_prompt = prompt.objects(id=id).first() 
            updated_prompt_json = updated_prompt.to_json()
            updated_prompt_dict = json.loads(updated_prompt_json)
            return jsonify({"message": "Prompt updated successfully", "updated_prompt": updated_prompt_dict}), 200
        except Exception as e:
            return jsonify({"Error": str(e)}), 50