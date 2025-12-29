from PIL import Image
import pyautogui
import cv2
import numpy as np
import pyscreeze
import os

pyscreeze.USE_IMAGE_NOT_FOUND_EXCEPTION = False

region_stake = {
	"dealer":(600, 530, 180, 18),
	"player":(900, 680, 180, 18),
	"player_split_1":(1000, 680, 180, 18),
	"player_split_2":(750, 680, 180, 18),
	"bet": "bet",
	"cards": "cards",
	"bcp": "bcp",
	"double":"double",
	"split": "split",
	"hit":"hit",
	"stand":"stand",
	"insurance_yes":"insurance_yes",
	"insurance_no":"insurance_no",
	"chip":"chip",
	"split": (1100, 535),
	"ll":"ll"
}

region_selected = region_stake

class Vision:
	def __init__(self):
		self.CONF = 0.92

	def get_state(self, split_state):
		img_dealer_cards = pyautogui.screenshot(region=region_selected["dealer"])

		player_region = region_selected["player"]
		if split_state == 1:
			player_region = region_selected["player_split_1"]
		elif split_state == 2:
			player_region = region_selected["player_split_2"]

		img_player_cards = pyautogui.screenshot(region=player_region)
		
		dealer_cv2 = cv2.cvtColor(np.array(img_dealer_cards), cv2.COLOR_BGR2RGB)
		player_cv2 = cv2.cvtColor(np.array(img_player_cards), cv2.COLOR_BGR2RGB)

		bet_sign_location = pyautogui.locateCenterOnScreen(Image.open(f'img/{region_selected["bet"]}.png'), confidence = 0.9)
		hit_location = pyautogui.locateCenterOnScreen(Image.open(f'img/{region_selected["hit"]}.png'), confidence = 0.9)
		stand_location = pyautogui.locateCenterOnScreen(Image.open(f'img/{region_selected["stand"]}.png'), confidence = 0.9)
		double_location = pyautogui.locateCenterOnScreen(Image.open(f'img/{region_selected["double"]}.png'), confidence = 0.75)
		insurance_yes_location = pyautogui.locateCenterOnScreen(Image.open(f'img/{region_selected["insurance_yes"]}.png'), confidence = 0.9)
		insurance_no_location = pyautogui.locateCenterOnScreen(Image.open(f'img/{region_selected["insurance_no"]}.png'), confidence = 0.9)
		burn_cards_location = pyautogui.locateCenterOnScreen(Image.open(f'img/{region_selected["bcp"]}.png'), confidence = 0.9)
		chip_location = pyautogui.locateCenterOnScreen(Image.open(f'img/{region_selected["chip"]}.png'), confidence = 0.9)
		ll_location = pyautogui.locateCenterOnScreen(Image.open(f'img/{region_selected["ll"]}.png'), confidence = 0.8)

		player_total = 0
		dealer_total = 0
		dealer_cards = []
		player_cards = []
		for i in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13):
			last_found_x = -1
			last_found_player_x = -1
			if os.path.exists(f'img/{region_selected["cards"]}/{i}b.png'):
				target_card = Image.open(f'img/{region_selected["cards"]}/{i}b.png')
				target_found_dealer = pyautogui.locateAll(target_card, img_dealer_cards, grayscale=False, confidence = self.CONF)
				target_found_player = pyautogui.locateAll(target_card, img_player_cards, grayscale=False, confidence = self.CONF)
				for found in target_found_dealer:
					if not abs(found.left - last_found_x) <= 5:
						dealer_total += min(i, 10)
						dealer_cards.append(i)
					last_found_x = found.left
				for found in target_found_player:
					if not abs(found.left - last_found_player_x) <= 5:
						player_total += min(i, 10)
						player_cards.append(i)
					last_found_player_x = found.left

			last_found_x = -1
			last_found_player_x = -1
			if os.path.exists(f'img/{region_selected["cards"]}/{i}r.png'):
				target_card = Image.open(f'img/{region_selected["cards"]}/{i}r.png')
				target_found_dealer = pyautogui.locateAll(target_card, img_dealer_cards, grayscale=False, confidence = self.CONF)
				target_found_player = pyautogui.locateAll(target_card, img_player_cards, grayscale=False, confidence = self.CONF)
				for found in target_found_dealer:
					if not abs(found.left - last_found_x) <= 5:
						dealer_total += min(i, 10)
						dealer_cards.append(i)
					last_found_x = found.left
				for found in target_found_player:
					if not abs(found.left - last_found_player_x) <= 5:
						player_total += min(i, 10)
						player_cards.append(i)
					last_found_player_x = found.left
					
		cv2.imwrite('state/dealer_cards.png', dealer_cv2)
		cv2.imwrite('state/player_cards.png', player_cv2)

		return {
			"dealer": dealer_total,
			"dealer_cards": dealer_cards,
			"player": player_total,
			"player_cards": player_cards,
			"bet_sign_location": bet_sign_location,
			"hit_location": hit_location,
			"stand_location": stand_location,
			"double_location": double_location,
			"insurance_yes_location":insurance_yes_location,
			"insurance_no_location":insurance_no_location,
			"burn_cards_location":burn_cards_location,
			"chip_location": chip_location,
			"ll_location": ll_location,
			"split": region_selected["split"],

		}
