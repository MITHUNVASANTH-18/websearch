from flask import Blueprint
from Controller.prompt_controller import PromptClass

prompt_Bp =Blueprint('prompt',__name__)

prompt_Bp.add_url_rule('/prompt', view_func=PromptClass.postPrompt, methods=['POST'])
prompt_Bp.add_url_rule('/getprompt', view_func=PromptClass.getPromptById, methods=['GET'])
prompt_Bp.add_url_rule('/editprompt', view_func=PromptClass.updatePrompt, methods=['PUT'])
