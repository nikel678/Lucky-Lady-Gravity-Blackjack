# LuckyLady-Gravity-Blackjack
Python automatic blackjack card counting bot for Gravity Blackjack.

Focuses on vulnerable side bet "Any 20 &amp; Queens".

Proof of Concept.


System Suggestions:
- Dual monitor setup (console on one monitor, game on other).
- 1920x1080 monitor (1080p).

Warning:
- Does not take into account the random burn cards as they do not matter, as if these are random this is the same as the cut card being put forward the amount of burned cards.
- Does not have perfect card information accuracy due to overhitters and splitters.
- Other hit bots are prevelant within Gravity Blackjack. These bots are counters but shorten the deck and ruin the game for themselves, find times where the rest of the people are playing with the book to keep accuracy higher. 
- Does not split aces due to accuracy factors, and there is no hit on aces after split.
- Does not include 16 vs 10 variation.
- split action does not have a reference image due to transparency. The x y location is hardcoded in region config located at the top of vision.py.
- Any 20 & Queens side bet is heavily more important than main bet due to higher potential advantage.
- Side bet max wager: 50 units.
- VARIANCE: due to possible side bet multipliers in gravity blackjack the resulting variance is heavily increased in comparison with a guaranteed paytable.
  

How to run:
- Install requirements.txt "pip install -r requirements.txt".
- Modify counter.py, change self.main_bet_max and self.luck_bet_max to fit bankroll.
- Setup cmd, run "python main.py".
- Default region is setup for stake us. Hamburger menu should be minimized to ensure dealer and player hand capture.
- Start program at start of a shoe.
- Check in every couple of hours to monitor long term live session issues.
- Has a possibility to miss burn cards sign due to to these issues, has failsafe to prevent damage.



How to fix (if needed):
- Images will need to be recaptured in certain cases. Gui change is common.
- Use cc.py and the web gui located at 127.0.0.1:777 to help debug.

