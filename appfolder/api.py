import requests as re
import os

get_url = f"https://world.openfoodfacts.org/api/v0/product/"
post_url = "https://world.openfoodfacts.org/cgi/product_jqm2.pl"
image_post_url = "https://world.openfoodfacts.org/cgi/product_image_upload.pl"


def call_api(code=3017624010701, params=None):

    response = re.get(get_url + f"{code}", params=params)
    print(response.url)

    response = response.json().get("product", None)

    if response:
        nutrition_score = response.get("nutriscore_score", "not found")
        nutrition_grade = response.get("nutrition_grades", "not found")
        nutrient_levels = response.get("nutrient_levels_tags", 0)
        print(
            f"Nutrition score: {nutrition_score}\nNutrition grade: {nutrition_grade}\nNutrient levels: {nutrient_levels}"
        )
        return response
    else:
        print("This product doesn't exist in the database")


def update_product(data):

    response = re.post(url=post_url, auth=("am2", "myopenfood123!"), data=data)

    return response


def post_image(data, image):
    response = re.post(
        url=image_post_url, auth=("am2", "myopenfood123!"), data=data, files=image
    )
    return response


new_product = 6156000092188  # Three crown milk QR code.

path_to_dir = os.path.dirname(__file__)

if __name__ == "main":
    with open(path_to_dir + "\\milk_ingredients.png", "rb") as image:
        data = {
            "code": new_product,
            "imagefield": "ingredients_en",
        }
        response = post_image(data=data, image={"imgupload_ingredients_en": image})
        print(response.json())

# list of nutriment fields
# Energy (kJ) *
# Energy (kcal)
# Fat *
# Saturated fat *
# g
# Carbohydrates
# g
# Sugars *
# g
# Fiber *
# g
# Proteins *
# g
# Salt *
# g
# Sodium
# g
# Alcohol
