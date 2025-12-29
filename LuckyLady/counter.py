from vision import Vision
import asyncio
import os
import math
import pyautogui
import sys

class ICounter:
	def __init__(self):
		self.main_bet_max = 8 #suggested 1 kelly at 1000 BR
		self.luck_bet_max = 50 #suggested 1:100 for 1 kelly - 50 is max on side bet. use 50 for 5000 BR, 10 for 1000 BR for 1 kelly

		self.ll_advantage_threshold = 1
		self.insurance_count_threshold = 1.5

		self.pair_splitting = {
			10: [False, False, False, False, ((-1, 5, False),(1, 5, True)), ((-1, 4, False),(1, 4, True)), False, False, False, False],
			9:  [False, True,  True,  True,  True,  True,  False, True,  True,  False],
			8:  [True,  True,  True,  True,  True,  True,  True,  True,  True,  True],
			7:  [False, True,  True,  True,  True,  True,  True,  False, False, False],
			6:  [False, True, True,  True,  True,  True,  False, False, False, False],
			5:  [False, False, False, False, False, False, False, False, False, False],
			4:  [False, False, False, False, True, True, False, False, False, False],
			3:  [False, True, True, True, True, True, True, False, False, False],
			2:  [False, True, True, True, True, True, True, False, False, False],
			1:  [False, False, False, False, False, False, False,  False,  False,  False] #splitting aces are nerfed online
		}

		self.hard_totals = {
			17: ["S", "S", "S", "S", "S", "S", "S", "S", "S", "S"],
			16: ["H", "S", "S", "S", "S", "S", "H", "H", "H", "H"],
			15: ["H", "S", "S", "S", "S", "S", "H", "H", "H", "H"],
			14: ["H", "S", "S", "S", "S", "S", "H", "H", "H", "H"],
			13: ["H", "S", "S", "S", "S", "S", "H", "H", "H", "H"],
			12: ["H", "H", "H", "S", "S", "S", "H", "H", "H", "H"],
			11: ["H", "D", "D", "D", "D", "D", "D", "D", "D", "H"],
			10: ["H", "D", "D", "D", "D", "D", "D", "D", "D", "H"],
			9:  ["H", "H", "D", "D", "D", "D", "H", "H", "H", "H"],
			8:  ["H", "H", "H", "H", "H", "H", "H", "H", "H", "H"],
		}
		self.soft_totals = {
			10: ["S", "S", "S", "S", "S", "S", "S", "S", "S", "S"],
			9:  ["S", "S", "S", "S", "S", "S", "S", "S", "S", "S"],
			8:  ["S", "S", "S", "S", "S", "S", "S", "S", "S", "S"],
			7:  ["H", "S", "D", "D", "D", "D", "S", "S", "H", "H"],
			6:  ["H", "H", "D", "D", "D", "D", "H", "H", "H", "H"],
			5:  ["H", "H", "H", "D", "D", "D", "H", "H", "H", "H"],
			4:  ["H", "H", "H", "D", "D", "D", "H", "H", "H", "H"],
			3:  ["H", "H", "H", "H", "D", "D", "H", "H", "H", "H"],
			2:  ["H", "H", "H", "H", "D", "D", "H", "H", "H", "H"],
			1:  ["H", "H", "H", "H", "D", "D", "H", "H", "H", "H"]
		}
		self.RRPC_card_values = {
			1: -4,
			2: 2,
			3: 3,
			4: 3,
			5: 4,
			6: 3,
			7: 2,
			8: 0,
			9: -1,
			10: -3,
			11: -3,
			12: -3,
			13: -3
		}
		self.WONG_card_values = {
			1: -1,
			2: 0.5,
			3: 1,
			4: 1,
			5: 1.5,
			6: 1,
			7: 0.5,
			8: 0,
			9: -0.5,
			10: -1,
			11: -1,
			12: -1,
			13: -1
		}
		self.IC_values = {
			10: -1,
			11: -1,
			12: -1, 
			13: -1, 
			1: 4/9,
			2: 4/9,
			3: 4/9,
			4: 4/9,
			5: 4/9,
			6: 4/9,
			7: 4/9,
			8: 4/9,
			9: 4/9
		}
		self.LL_values = {
			10: 1/12,
			11: 1/12,
			12: -1, 
			13: 1/12, 
			1: 1/12,
			2: 1/12,
			3: 1/12,
			4: 1/12,
			5: 1/12,
			6: 1/12,
			7: 1/12,
			8: 1/12,
			9: 1/12
		}
		self.AN_values = {
			10: 2/11,
			11: 2/11,
			12: 2/11, 
			13: 2/11, 
			1: -1,
			2: 2/11,
			3: 2/11,
			4: 2/11,
			5: 2/11,
			6: 2/11,
			7: 2/11,
			8: 2/11,
			9: -1
		}
		self.HL_values = {
			10: -1,
			11: -1,
			12: -1, 
			13: -1, 
			1: -1,
			2: 1,
			3: 1,
			4: 1,
			5: 1,
			6: 1,
			7: 0,
			8: 0,
			9: 0
		}


		self.INSTATES = [
			"PREBET",
			"PLACEBET",
			"PLACEDBET",
			"CARDSOUT",
			"INSURANCE",
			"DECISION",
			"ARMAGEDON",
			"SPLIT",
		]
		self.active = True
		self.state = {}
		self.vision = Vision()
		self.seen_cards = []
		self.restart_counter()
		self.split_state = 0
		self.hand_history = []
		self.mess_up_count = 0


	def restart_counter(self):
		if self.seen_cards != []:
			self.hand_history.append(self.seen_cards)
		self.seen_cards = []
		self.dealer_hand_last = []
		self.player_hand_last = []
		self.player_split_hand_1 = []
		self.player_split_hand_2 = []
		self.instate = self.INSTATES[0]
		self.after_first = False
		self.last_click_amt = 0
		self.last_hit_card_len = 0

	async def update_state_loop(self):
		while self.active:
			await self.update_instate()
			self.update_seen_cards()
			self.print_state()
			await asyncio.sleep(0.1)

	def glitch_fix(self):
		self.after_first = False
		self.split_state = 0
		self.last_hit_card_len = 0
		self.mess_up_count += 1
		self.player_hand_last = []
		self.instate = "PREBET"

	async def update_instate(self):
		self.state = self.vision.get_state(self.split_state)
		if self.state["burn_cards_location"]:
			self.restart_counter()
		match self.instate:
			case "PREBET":
				self.after_first = False
				self.last_hit_card_len = 0
				self.split_state = 0
				if self.state["chip_location"]:
					self.action_click_chip()
				if self.state["bet_sign_location"]:
					self.instate = "PLACEBET"
			case "PLACEBET":
				click_amount = self.tc_to_click_amount()
				self.last_click_amt = click_amount
				bet_sign_loc = self.state["bet_sign_location"]
				for i in range(click_amount):
					await asyncio.sleep(0.02)
					pyautogui.click(self.state["bet_sign_location"])
				combined_count = self.new_calc_combined_count()
				if (combined_count >= self.ll_advantage_threshold) and self.state["ll_location"]:
					ll_click_amount = self.ll_to_click_amount()
					for i in range(ll_click_amount):
						await asyncio.sleep(0.02)
						pyautogui.click(self.state["ll_location"])
				self.instate = "PLACEDBET"
			case "PLACEDBET":
				if len(self.state["player_cards"]) != 0 or len(self.state["dealer_cards"]) != 0:
					self.instate = "CARDSOUT"
			case "CARDSOUT":
				if len(self.state["dealer_cards"]) == 1 and self.state["dealer_cards"][0] == 1:
					self.instate = "INSURANCE"
				elif len(self.state["dealer_cards"]) == 1 and len(self.state["player_cards"]) == 2:
					self.instate = "DECISION"
				elif len(self.state["player_cards"]) == 0 and len(self.state["dealer_cards"]) == 0:
					self.glitch_fix()
					return
			case "INSURANCE":
				
				if len(self.state["player_cards"]) == 0 and len(self.state["dealer_cards"]) == 0:
					self.glitch_fix()
					return
				elif self.get_IC_count() >= self.insurance_count_threshold:
					if self.action_insurance_take():
						self.instate = "DECISION"
				else:
					if self.action_insurance_refuse():
						self.instate = "DECISION"

			case "DECISION":
				if self.state["bet_sign_location"]:
					self.instate = "PREBET"
					
				#bj edge case
				if len(self.state["dealer_cards"]) == 2 and self.state["dealer_cards"][0] == 1 and self.state["dealer_cards"][1] in (10, 11, 12, 13):
					self.instate = "ARMAGEDON"
					return

				if len(self.state["player_cards"]) >= 2 and len(self.state["dealer_cards"]) >= 1 and len(self.state["player_cards"]) > self.last_hit_card_len:
					match self.get_decision():
						case "A":
							self.split_or_armagedon()
						case "S":
							if self.action_stand():
								self.split_or_armagedon()
						case "H":
							if self.action_hit():
								self.instate = "DECISION"
								self.after_first = True
								self.last_hit_card_len = len(self.state["player_cards"])
						case "D":
							if self.after_first:
								dealer_shown_val = min(self.state["dealer_cards"][0], 10)
								second_sum = 0
								for card in self.state["player_cards"][1:]:
									second_sum += min(card, 10)
								if self.state["player_cards"][0] == 1 and second_sum == 7 and (1 < dealer_shown_val < 9):
									if self.action_stand():
										self.split_or_armagedon()
								else:
									if self.action_hit():
										self.instate = "DECISION"
										self.last_hit_card_len = len(self.state["player_cards"])
							else:
								if self.action_double():
									self.split_or_armagedon()
						case "SP":
							self.instate = "SPLIT"

			case "SPLIT":
				if len(self.state["player_cards"]) == 0 and len(self.state["dealer_cards"]) == 0:
					self.glitch_fix()
					return
				if len(self.state["dealer_cards"]) == 2 and self.state["dealer_cards"][0] == 1 and self.state["dealer_cards"][1] in (10, 11, 12, 13):
					self.instate = "ARMAGEDON"
					return
				if self.action_split():
					self.player_split_hand_1 = []
					self.player_split_hand_2 = []
					self.split_state = 1
					self.player_hand_last = []
					self.after_first = False
					self.last_hit_card_len = 0
					self.instate = "DECISION"

			case "ARMAGEDON":
				if len(self.state["dealer_cards"]) > 1 or self.state["bet_sign_location"]:
					self.instate = "PREBET"

	def split_or_armagedon(self):
		if self.split_state == 1:
			self.split_state = 2
			self.after_first = False
			self.instate = "DECISION"
			self.player_split_hand_1 = []
			self.last_hit_card_len = 0
			self.player_hand_last = []
		else:
			if self.split_state == 2:
				self.split_state = 0
				self.player_split_hand_2 = self.player_hand_last[:]
				self.last_hit_card_len = 0
			self.player_hand_last = []
			self.instate = "ARMAGEDON"

	def action_insurance_take(self):
		if self.state["insurance_yes_location"] is None:
			return False
		pyautogui.click(self.state["insurance_yes_location"])
		return True

	def action_insurance_refuse(self):
		if self.state["insurance_no_location"] is None:
			return False
		pyautogui.click(self.state["insurance_no_location"])
		return True

	def action_stand(self):
		if self.state["stand_location"] is None:
			return False
		pyautogui.click(self.state["stand_location"])
		return True

	def action_hit(self):
		if self.state["hit_location"] is None:
			return False
		pyautogui.click(self.state["hit_location"])
		return True

	def action_double(self):
		if self.state["double_location"] is None:
			return False
		pyautogui.click(self.state["double_location"])
		return True

	def action_split(self):
		if self.state["hit_location"] is None:
			return False
		pyautogui.click(x=self.state["split"][0],y=self.state["split"][1])
		return True

	def action_click_chip(self):
		if self.state["chip_location"] is None:
			return False
		pyautogui.click(self.state["chip_location"])
		return True



	def get_decision(self):
		dealer_shown_val = min(self.state["dealer_cards"][0] - 1, 9)
		player_hand_val = 0
		for card in self.state["player_cards"]:
			player_hand_val += min(card, 10)

		if player_hand_val >= 21:
			return "A"

		if len(self.state["player_cards"]) == 2 and  min(self.state["player_cards"][0], 10) == min(self.state["player_cards"][1], 10) and self.split_state == 0:
			split_decision = self.pair_splitting[player_hand_val/2][dealer_shown_val]
			if isinstance(split_decision, bool):
				if split_decision:
					return "SP"
			elif isinstance(split_decision, tuple):
				var_1 = split_decision[0]
				var_2 = split_decision[1]
				current_count = self.get_RRPC_count()
				if var_1[0] == -1:
					if var_1[1] >= current_count:
						if var_1[2]:
							return "SP"
					else:
						if var_2[2]:
							return "SP"
				elif var_1[0] == 1:
					if var_1[1] <= current_count:
						if var_1[2]:
							return "SP"
					else:
						if var_2[2]:
							return "SP"

		if 1 == self.state["player_cards"][0]:
			non_ace = 0
			for card in self.state["player_cards"][1:]:
				non_ace += min(card, 10)
			if non_ace == 10:
				return "A"
			if non_ace >= 11:
				if player_hand_val >= 18:
					return "S"
				return self.hard_totals[player_hand_val][dealer_shown_val]
			return self.soft_totals[non_ace][dealer_shown_val]
		else:
			if player_hand_val >= 18:
				return "S"
			elif player_hand_val <= 7:
				return "H"
			return self.hard_totals[player_hand_val][dealer_shown_val]

	def print_state(self):
		seen_decks = round(len(self.seen_cards)/52, 2)
		new_combined_count = self.new_calc_combined_count()
		seen_cards_total = len(self.seen_cards) + len(self.dealer_hand_last) + len(self.player_hand_last) + len(self.player_split_hand_1) + len(self.player_split_hand_2)
		rrpc_count = self.get_RRPC_count()
		itc_count = self.get_IC_count()
		seen_queens = self.get_seen_queens()
		seen_tens = self.get_seen_tens()
		seen_aces = self.get_seen_aces()
		seen_nines = self.get_seen_nines()

		soft_20_chance = self.soft_20_chance(seen_cards_total, seen_aces, seen_nines)
		hard_20_chance = self.hard_20_chance(seen_cards_total, seen_tens)
		any_queens_chance = self.any_queens_chance(seen_cards_total, seen_queens)

		chance_for_10 = ((128-seen_tens)/(416-seen_cards_total))

		total_chance = hard_20_chance + any_queens_chance * (1-chance_for_10) + soft_20_chance


		os.system('cls')
		for state in self.state:
			print(f"{state}: {self.state[state]}")
		print("-------------")
		print(f"Instate {self.instate}")
		#hl_tc = self.get_HL_count()
		#lltc_count = self.get_LL_count()
		#an_count = self.get_AN_count()
		print("DP", f"{seen_decks}/8 ({int(seen_decks/8 * 100)}%)")
		print("TC", rrpc_count)
		print("ITC", itc_count)
		print("IRTP", f"{99.46 + rrpc_count * 0.6:.2f}%")
		print("QRTP", f"{100 + new_combined_count:.2f}%")
		print(f"Take Insurance {'Yes' if itc_count >= 1.5 else 'No'}")
		#print("WONG", self.get_WONG_count())
		#print("HLTC", hl_tc)
		#print("LLTC", lltc_count)
		#print("ANTC", an_count)
		print(f"Click Amount {self.last_click_amt}")
		print("Mess Up Count", self.mess_up_count)
		print(f"Cards {seen_cards_total}")
		print(f"{seen_cards_total/(52 * 2.5)*100:.2f}% of 2.5 decks")
		print("-------------")
		print("Chance")
		print(f"Any Queens {any_queens_chance*100:.2f}%")
		print(f"Hard 20 {hard_20_chance*100:.2f}%")
		print(f"Soft 20 {soft_20_chance*100:.2f}%")
		print(f"Total {total_chance*100:.2f}%")
		print(f"Original {20.855:.2f}%")
		print(f"CADV {((total_chance*100 - 20.855)/20.855)*100:.2f}%")
		print("-------------")
		print(self.seen_cards, self.dealer_hand_last, self.player_hand_last, self.player_split_hand_1, self.player_split_hand_2)

	def update_seen_cards(self):
		if self.state["dealer_cards"] != [] and len(self.state["dealer_cards"]) > len(self.dealer_hand_last):
			self.dealer_hand_last = self.state["dealer_cards"]
		if self.state["player_cards"] != [] and len(self.state["player_cards"]) > len(self.player_hand_last):
			self.player_hand_last = self.state["player_cards"]
		if len(self.state["dealer_cards"]) == 0 and len(self.state["player_cards"]) == 0:
			new_entry = []
			new_entry.extend(self.dealer_hand_last)
			new_entry.extend(self.player_hand_last)
			new_entry.extend(self.player_split_hand_1)
			new_entry.extend(self.player_split_hand_2)
			self.seen_cards.extend(new_entry)
			self.dealer_hand_last.clear()
			self.player_hand_last.clear()
			self.player_split_hand_1.clear()
			self.player_split_hand_2.clear()

			if len(self.seen_cards) > 178: #hotfix for burn card misshap, failsafe is dynamic with the deck cut
				print("TOO MANY CARDS, BURN CARDS NOT DETECTED")
				sys.exit()

	def get_decks_left(self):
		return (416-len(self.seen_cards)) / 52

	def get_WONG_count(self):
		count = 0
		for card in self.seen_cards:
			count += self.WONG_card_values[card]
		for card in self.dealer_hand_last:
			count += self.WONG_card_values[card]
		for card in self.player_hand_last:
			count += self.WONG_card_values[card]
		for card in self.player_split_hand_1:
			count += self.WONG_card_values[card]
		for card in self.player_split_hand_2:
			count += self.WONG_card_values[card]
		true_count = round(count / self.get_decks_left(), 2)

		return true_count

	def get_RRPC_count(self):
		count = 0
		for card in self.seen_cards:
			count += self.RRPC_card_values[card]
		for card in self.dealer_hand_last:
			count += self.RRPC_card_values[card]
		for card in self.player_hand_last:
			count += self.RRPC_card_values[card]
		for card in self.player_split_hand_1:
			count += self.RRPC_card_values[card]
		for card in self.player_split_hand_2:
			count += self.RRPC_card_values[card]
		true_count = round(count / (self.get_decks_left() * 3), 2)

		return true_count

	def get_IC_count(self):
		count = 0
		for card in self.seen_cards:
			count += self.IC_values[card]
		for card in self.dealer_hand_last:
			count += self.IC_values[card]
		for card in self.player_hand_last:
			count += self.IC_values[card]
		for card in self.player_split_hand_1:
			count += self.IC_values[card]
		for card in self.player_split_hand_2:
			count += self.IC_values[card]

		true_count = round(count / self.get_decks_left(), 2)
		return true_count

	def get_LL_count(self):
		count = 0
		for card in self.seen_cards:
			count += self.LL_values[card]
		for card in self.dealer_hand_last:
			count += self.LL_values[card]
		for card in self.player_hand_last:
			count += self.LL_values[card]
		for card in self.player_split_hand_1:
			count += self.LL_values[card]
		for card in self.player_split_hand_2:
			count += self.LL_values[card]

		true_count = round(count / self.get_decks_left(), 2)
		return true_count

	def get_AN_count(self):
		count = 0
		for card in self.seen_cards:
			count += self.AN_values[card]
		for card in self.dealer_hand_last:
			count += self.AN_values[card]
		for card in self.player_hand_last:
			count += self.AN_values[card]
		for card in self.player_split_hand_1:
			count += self.AN_values[card]
		for card in self.player_split_hand_2:
			count += self.AN_values[card]

		true_count = round(count / self.get_decks_left(), 2)
		return true_count

	def get_HL_count(self):
		count = 0
		for card in self.seen_cards:
			count += self.HL_values[card]
		for card in self.dealer_hand_last:
			count += self.HL_values[card]
		for card in self.player_hand_last:
			count += self.HL_values[card]
		for card in self.player_split_hand_1:
			count += self.HL_values[card]
		for card in self.player_split_hand_2:
			count += self.HL_values[card]

		true_count = round(count / self.get_decks_left(), 2)
		return true_count

	#depricated
	def calc_combined_count(self):
		an_count = self.get_AN_count()
		lltc_count = self.get_LL_count()
		itc_count = self.get_IC_count()
		
		x = itc_count
		z = lltc_count
		y = an_count

		t = (((128 / (416 - 18 * x)) * (127 / (415 - 18 * x))) / ((128/416) * (127/415))) * 0.9466 - 1
		q = ((1 - (1 - 32 / (416 - 96 * z)) * (1 - 32 / (415 - 96 * z)))/(1 - (1 - 32 / 416) * (1 - 32 / 415))) * 0.9466 - 1
		a = (((32 * 32) / ((416 - 44 * y) * (415 - 44 * y))) / ((32 * 32) / (416 * 415))) * 0.9466 - 1

		if z < 0:
			q = ((1 - (1 - (32 + 8 * z) / 416) * (1 - (32 + 8 * z) / 415))/(1 - (1 - 32 / 416) * (1 - 32 / 415))) * 0.9466 - 1

		if x < 0:
			t = (((128 + 8 * x) / 416) * ((127 + 8 * x) / 415) / ((128/416) * (127/415))) * 0.9466 - 1

		bet_amount =  t * 0.69 + q * 0.25 + a * 0.06

		return bet_amount * 100

	def get_seen_tens(self):
		seen_tens = 0
		for card in self.seen_cards:
			if card >= 10:
				seen_tens += 1
		for card in self.dealer_hand_last:
			if card >= 10:
				seen_tens += 1
		for card in self.player_hand_last:
			if card >= 10:
				seen_tens += 1
		for card in self.player_split_hand_1:
			if card >= 10:
				seen_tens += 1
		for card in self.player_split_hand_2:
			if card >= 10:
				seen_tens += 1
		return seen_tens

	def get_seen_queens(self):
		seen_queens = 0
		for card in self.seen_cards:
			if card == 12:
				seen_queens += 1
		for card in self.dealer_hand_last:
			if card == 12:
				seen_queens += 1
		for card in self.player_hand_last:
			if card == 12:
				seen_queens += 1
		for card in self.player_split_hand_1:
			if card == 12:
				seen_queens += 1
		for card in self.player_split_hand_2:
			if card == 12:
				seen_queens += 1
		return seen_queens

	def get_seen_aces(self):
		seen_aces = 0
		for card in self.seen_cards:
			if card == 1:
				seen_aces += 1
		for card in self.dealer_hand_last:
			if card == 1:
				seen_aces += 1
		for card in self.player_hand_last:
			if card == 1:
				seen_aces += 1
		for card in self.player_split_hand_1:
			if card == 1:
				seen_aces += 1
		for card in self.player_split_hand_2:
			if card == 1:
				seen_aces += 1
		return seen_aces

	def get_seen_nines(self):
		seen_nines = 0
		for card in self.seen_cards:
			if card == 9:
				seen_nines += 1
		for card in self.dealer_hand_last:
			if card == 9:
				seen_nines += 1
		for card in self.player_hand_last:
			if card == 9:
				seen_nines += 1
		for card in self.player_split_hand_1:
			if card == 9:
				seen_nines += 1
		for card in self.player_split_hand_2:
			if card == 9:
				seen_nines += 1
		return seen_nines


	def soft_20_chance(self, seen_cards, seen_aces, seen_nines):
		chance = 2 * ((32 - seen_aces) * (32 - seen_nines)) / ((416 - seen_cards) * (415 - seen_cards))
		return chance

	def hard_20_chance(self, seen_cards, seen_tens):
		chance = (((128 - seen_tens) / (416 - seen_cards)) * ((127 - seen_tens) / (415 - seen_cards)))
		return chance

	def any_queens_chance(self, seen_cards, seen_queens):
		chance = (1 - (1 - (32 - seen_queens) / (416 - seen_cards)) * (1 - (32 - seen_queens) / (415 - seen_cards)))
		return chance

	def soft_20_advantage(self, seen_cards, seen_aces, seen_nines):
		original_chance = 2 * ((32 * 32) / (416 * 415))
		soft_20_chance = self.soft_20_chance(seen_cards, seen_aces, seen_nines)
		a = (soft_20_chance / original_chance) * 0.9466 - 1
		return a

	def hard_20_advantage(self, seen_cards, seen_tens):
		original_chance = ((128/416) * (127/415))
		hard_20_chance = self.hard_20_chance(seen_cards, seen_tens)
		t = (hard_20_chance / original_chance) * 0.9466 - 1
		return t

	def any_queens_advantage(self, seen_cards, seen_queens):
		original_chance = (1 - (1 - 32 / 416) * (1 - 32 / 415))
		any_queens_chance = self.any_queens_chance(seen_cards, seen_queens)
		q = (any_queens_chance / original_chance) * 0.9466 - 1
		return q


	def new_calc_combined_count(self):
		seen_cards = len(self.seen_cards) + len(self.dealer_hand_last) + len(self.player_hand_last) + len(self.player_split_hand_1) + len(self.player_split_hand_2)
		seen_tens = self.get_seen_tens()
		seen_queens = self.get_seen_queens()
		seen_aces = self.get_seen_aces()
		seen_nines = self.get_seen_nines()

		hard_20 = self.hard_20_advantage(seen_cards, seen_tens)
		any_queen = self.any_queens_advantage(seen_cards, seen_queens)
		soft_20 = self.soft_20_advantage(seen_cards, seen_aces, seen_nines)

		#weights estimated on paytable and multipliers.
		bet_amount =  hard_20 * 0.70 + any_queen * 0.23 + soft_20 * 0.07

		return bet_amount * 100

	def tc_to_click_amount(self):
		rrpc_count = self.get_RRPC_count()
		rrpc_click_amount = min(self.main_bet_max, max(int(4 * (rrpc_count-1)), 1))
		return rrpc_click_amount

	def ll_to_click_amount(self):
		advantage = self.new_calc_combined_count() # 1% adv $1 - 2% adv $2 - 3% adv $4 - 4% adv $8 - 5% adv $16 - 6% adv - $32 7% adv - $50
		click_amount = max(min(self.luck_bet_max, int(2 ** (advantage - 1))), 1) #prevents error in early advantage, bets most during 4-7% and still places some during 1-4%

		return click_amount
