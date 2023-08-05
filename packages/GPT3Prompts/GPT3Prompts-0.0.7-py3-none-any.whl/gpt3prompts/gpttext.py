#user_input = input('Input Artist  :  ')
#input_object = input('Input Object  :  ')
#API_KEY = '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'
def generation(user_input,input_object,API_KEY):
    import openai
    #import pyttsx3
    #from api_key import API_KEY
    openai.api_key = API_KEY
   # conversation = ""
    #while True:
        #try:
           # user_input = r.recognize_google(audio)
            #print('\n')
           # user_input = input('Input Artist  :  ')
            #input_object = input('Input Object  :  ')
    user_input = user_input
    input_object = input_object
        #except:
            #continue

    prompts ="Write a text prompt about detailed "+input_object+" for a AI art generation software that would fit the art style of "+user_input + "\n"
        #prompt = user_name + ": " + user_input + "by style John Blanche"+"\n"

        #conversation += prompt
    response = openai.Completion.create(model='text-davinci-002', prompt=prompts,temperature=1, max_tokens=250)
    response_str = response["choices"][0]["text"].replace("\n", "")
        #print("The best prompts for your portrait is :\n\n",response_str + 'by style '+user_input)
    response_str = response_str.replace(".", ",")
        #response_str = response_str.split(user_name + ": ", 1)[0].split("", 1)[0]
        #conversation += response_str + "\n"
    print('\n')
        #print('\n')
    print("The best prompts for your portrait is :\n\n",response_str + 'by style '+user_input  