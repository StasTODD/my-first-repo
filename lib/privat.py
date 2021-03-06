import asyncio
import ast
from typing import List, Dict, Union, Any
from PIL import Image, ImageDraw, ImageFont
from .help_functions import get_json_from_web, create_dir


# Privatbank API (JSON format)
url_privatbank_private = "https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5"
url_privatbank_busines = "https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11"
url_privatbank_list = [url_privatbank_private, url_privatbank_busines]


async def get_jsons_privat(url_list: List[str]) -> list:
    coroutines = map(get_json_from_web, url_list)
    return await asyncio.gather(*coroutines)


async def parse_privat_jsons(raw_data: List[Dict[str, Union[int, str]]]) -> List[Dict[str, str]]:
    """
    :param raw_data: [{'status': 200,
                       'result': '[{"ccy":"USD","base_ccy":"UAH","buy":"26.85000","sale":"27.25000"}, ...]'},
                      {'status': 200,
                       'result': '[{"ccy":"USD","base_ccy":"UAH","buy":"26.90000","sale":"27.24796"}, ...]'}]

    :return [{'ccy': 'USD', 'base_ccy': 'UAH', 'buy': '26.85000', 'sale': '27.25000'},
             {'ccy': 'USD', 'base_ccy': 'UAH', 'buy': '26.90000', 'sale': '27.24796'}]
    """
    # Check correct result request and rebuild list with data:
    raw_data = [row["result"] for row in raw_data if row.get("result") and row.get("status") == 200]
    # Transform str -> List[Dict[str, str]] using ast.literal_eval method:
    raw_data = [ast.literal_eval(row) for row in raw_data]
    # Taking USD only:
    raw_data = [[currency for currency in row if currency.get("ccy") == "USD"][0] for row in raw_data]
    return raw_data


async def create_privat_currency_message(currency: List[Dict[str, str]], text_for_image: bool = False) -> str:
    """
    Create string with currency data

    Func arg position 0 - for retail
    Func arg position 1 - for business

    :param text_for_image: True/False
    :param currency: [{'ccy': 'USD', 'base_ccy': 'UAH', 'buy': '26.85000', 'sale': '27.25000'},
                      {'ccy': 'USD', 'base_ccy': 'UAH', 'buy': '26.90000', 'sale': '27.24796'}]
    :return: 'str'
    """
    if not isinstance(currency, list):
        return "Haven't data..."

    retail_buy = currency[0]["buy"]
    retail_sell = currency[0]["sale"]
    business_buy = currency[1]["buy"]
    business_sell = currency[1]["sale"]

    if not text_for_image:
        currency_str = f"Retail:\n" \
                       f"BUY USD: {retail_buy} UAH\n" \
                       f"SELL USD: {retail_sell} UAH\n" \
                       f"\n" \
                       f"Business:\n" \
                       f"BUY USD: {business_buy} UAH\n" \
                       f"SELL USD: {business_sell} UAH\n"
        return currency_str
    else:
        currency_str = f"Retail:\n\n" \
                       f"BUY USD: {retail_buy} UAH\n\n" \
                       f"SELL USD: {retail_sell} UAH\n\n" \
                       f"\n\n" \
                       f"Business:\n\n" \
                       f"BUY USD: {business_buy} UAH\n\n" \
                       f"SELL USD: {business_sell} UAH\n\n"
        return currency_str


async def create_privat_image(displayed_text: str) -> str:
    """
    Create images with text and return path to images

    :param displayed_text: str
    :return: "images/out/usd.png"
    """
    template_directory = "images/background_template"
    result_directory = "images/out"
    image_name = "usd.png"
    image_template_path = f"{template_directory}/{image_name}"
    image_result_path = f"{result_directory}/{image_name}"
    image_template = Image.open(image_template_path)
    draw = ImageDraw.Draw(image_template)

    font_size = 60
    font = ImageFont.truetype("images/fonts/Spartan/static/Spartan-SemiBold.ttf", size=font_size)

    # Start position on images:
    (x, y) = (190, 100)

    text_color = "rgb(0, 0, 0)"

    draw.text((x, y), displayed_text, fill=text_color, font=font)
    try:
        image_template.save(image_result_path)
    except FileNotFoundError:
        create_dir(result_directory)
        image_template.save(image_result_path)

    return image_result_path

__all__ = ["url_privatbank_list",
           "get_jsons_privat",
           "parse_privat_jsons",
           "create_privat_currency_message",
           "create_privat_image"]
