import json

#creating dictionary for selecting selector
preferences_decode = {
    "1": "xpath",
    "2": "id",
    "3": "name",
    "4": "css",
    "5": "linkText"
}

#code to wait until page loading
webdriver_wait_code = "WebDriverWait(driver, 15).until(move_to_element_to_be_clickable(({by}, '{value}')))\n"

#convert string to int
def int_convertor(to_convert):
    try:
        return int(to_convert)
    except Exception:
        return False

#convert selector name to its selenium version
def target_processor(target: str):
    by = "By."
    if target.startswith("name="):
        by += "NAME"
    elif target.startswith("xpath="):
        by += "XPATH"
    elif target.startswith("css="):
        by += "CSS_SELECTOR"
    elif target.startswith("id="):
        by += "ID"
    elif target.startswith("linkText="):
        by += "LINK_TEXT"
    value = target.split('=', maxsplit=1)[1]
    return [by, value]


#generate find_element code from target
def target_to_command(target: str):
    by, value = target_processor(target)
    value=value.replace('\'','\\\'') #prevent slashes from closing quotes
    return f"driver.find_element({by}, '{value}')"



#generate code for one command
def command_to_code(command_dict: dict, use_default: bool, preferences: str, manual_select=None):
    command = command_dict["Command"]
    value = command_dict["Value"]
    value = value.replace('\'', '\\\'') #prevent slashes from closing quotes
    if manual_select==None:
        target = get_target(command_dict, use_default, preferences)
    final_command = ""

    if command == "open":
        target = target.replace('\'', '\\\'') #prevent slashes from closing quotes
        final_command = f"driver.get('{target}')"
    elif command == "type":
        if manual_select!=None:
            target=manual_select
        by, value_ = target_processor(target)
        value_ = value_.replace('\'', '\\\'') #prevent slashes from closing quotes
        target = target.replace('\'', '\\\'') #prevent slashes from closing quotes
        final_command = f"{webdriver_wait_code.format(by=by, value=value_)}" \
                        f"element={target_to_command(target)}\n" \
                        f"element.clear()\n" \
                        f"element.send_keys('{value}')"
    elif command == "clickAndWait" or command == "click":
        if manual_select!=None:
            target=manual_select
        by, value = target_processor(target)
        value = value.replace('\'', '\\\'') #prevent slashes from closing quotes
        target = target.replace('\'', '\\\'') #prevent slashes from closing quotes
        final_command = f"{webdriver_wait_code.format(by=by, value=value)}" \
                        f"{target_to_command(target)}.click()"
    return final_command

def get_target(command: dict, use_default: bool, preferences: str):
    if "Targets" not in command.keys() or use_default:
        return command["Target"]
    else:
        target = None
        if preferences != ["0"]:
            for j in preferences:
                for i in command["Targets"]:
                    if i.startswith(preferences_decode[j]):
                        target = i
                        break
                if target != None:
                    break
        if target == None:
            target = command["Target"]
        return target

#importing requirements from selenium and defining function that helps to wait until page loads
result = '''#Generated using convertor by t.me/cryptopidval
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webdriver import WebElement
from selenium.webdriver.common.action_chains import ActionChains



def move_to_element_to_be_clickable(mark):
    def _predicate(driver):
        target = mark
        if not isinstance(target, WebElement):  # if given locator instead of WebElement
            target = driver.find_element(*target)  # grab element at locator
        try:
            actions = ActionChains(driver)
            actions.move_to_element(target).perform()
        except:
            return False
        target = expected_conditions.visibility_of(target)(driver)
        if target and target.is_enabled():
            return target
        return False

    return _predicate
    

driver = webdriver.Chrome()


'''
with open(input("Enter json filename: ")) as file:
    json_dict = json.load(file)

output = input("Enter output filename: ")


use_default_tagets = input("Do you want to use default targets(y/n)?: ").lower() == "y"
manual_mode=False
if not use_default_tagets:
    preferences = ""
    while sorted(preferences) not in [['1', '2', '3', '4'], ["0"]]:
        preferences = input("Set your prefernces, please.\n"
                            "1. xpath\n"
                            "2. id\n"
                            "3. name\n"
                            "4. css\n"
                            "5. linkText\n"
                            "For example 1234.\n"
                            "Or 0 if you want to select by yourself.\n")
else:
    preferences = "0"

if preferences == "0" and not use_default_tagets:
    manual_mode=True


if not manual_mode:
    for i in json_dict["Commands"]:
        result += command_to_code(i, use_default_tagets, preferences)
        result += "\n\n"
else:
    for i in json_dict["Commands"]:
        if "Targets" in i.keys():
            manual_select = ""
            t=0
            print(i)
            targets = "\n".join([f"{m+1}. {n}" for m,n in enumerate(i["Targets"])])
            while int_convertor(manual_select) not in range(1,len(i["Targets"])+1):
                if t==0:
                    t=1
                else:
                    print("Please try again.")
                manual_select=input(f"{targets}\n"
                      f"Please select target.\n")
            manual_select = i["Targets"][int(manual_select)-1]
            result += command_to_code(i, use_default_tagets, preferences, manual_select=manual_select)

        else:
            result += command_to_code(i, use_default_tagets, preferences)

        result += "\n\n"

result+="\n\ndriver.quit()"

with open(output, "w") as file:
    file.write(result)

