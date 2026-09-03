from datetime import datetime, timedelta
import difflib
import glob
import json
import math
import os
import random
import re
import sqlite3
from collections import Counter


class SmartIntentClassifier:
    """V3.6 Enhanced Intent Classifier Engine with Bigram Weights"""

    def __init__(self):
        self.intent_words = {}
        self.intent_bigrams = {}

    def tokenize(self, text):
        words = re.findall(r"\w+", text.lower())
        ignore = {"bhai", "bro", "oo", "ooo", "aa", "aah"}
        filtered = [w for w in words if w not in ignore]
        return filtered if filtered else words

    def get_bigrams(self, tokens):
        return [f"{tokens[i]} {tokens[i+1]}" for i in range(len(tokens) - 1)]

    def train(self, memory_db):
        self.intent_words = {}
        self.intent_bigrams = {}

        if not isinstance(memory_db, list):
            return

        for item in memory_db:
            if not isinstance(item, dict):
                continue

            tag = item.get("tag")
            patterns = item.get("patterns", [])
            words_list = []
            bigrams_list = []

            for p in patterns:
                tokens = self.tokenize(p)
                words_list.extend(tokens)
                bigrams_list.extend(self.get_bigrams(tokens))

            if tag not in self.intent_words:
                self.intent_words[tag] = Counter(words_list)
                self.intent_bigrams[tag] = Counter(bigrams_list)
            else:
                self.intent_words[tag].update(words_list)
                self.intent_bigrams[tag].update(bigrams_list)

    def predict_intent(self, text, threshold=0.20):
        tokens = self.tokenize(text)
        bigrams = self.get_bigrams(tokens)

        if not tokens or not self.intent_words:
            return None, 0.0

        best_tag = None
        max_score = 0.0

        for tag, counts in self.intent_words.items():
            total_words = sum(counts.values())
            if total_words == 0:
                continue

            score = 0.0
            for token in tokens:
                if token in counts:
                    score += (counts[token] / total_words) * 1.5

            bigram_counts = self.intent_bigrams.get(tag, Counter())
            for bg in bigrams:
                if bg in bg:
                    score += 2.0

            score = score / (len(tokens) ** 0.4)

            if score > max_score:
                max_score = score
                best_tag = tag

        if max_score >= threshold:
            return best_tag, max_score
        return None, 0.0


class MainAIEngine:

    def __init__(self, user_name="Pankaj"):
        self.user_name = user_name.strip().lower()
        self.session_history = []
        self.last_unknown_query = None

        self.current_context = None
        self.last_responses = {}

        self.ram_image_context = None

        self.db_name = "knowledge.db"
        self.init_sqlite_db()

        self.memory_file = self.handle_smart_memory_file()
        self.memory_db = []

        self.classifier = SmartIntentClassifier()
        self.load_memory()

    def init_sqlite_db(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tech_knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT UNIQUE,
                definition TEXT
            )
        """
        )

        cursor.execute("SELECT COUNT(*) FROM tech_knowledge")
        if cursor.fetchone()[0] == 0:
            defaults = [
                (
                    "cpu",
                    "CPU (Central Processing Unit) computer ka brain hota hai jo saari calculations aur instructions execute karta hai.",
                ),
                (
                    "ram",
                    "RAM (Random Access Memory) temporary memory hoti hai jo open apps aur active tasks ko fast run karti hai.",
                ),
                (
                    "python",
                    "Python ek high-level, interpreted programming language hai jo AI, Web Dev aur Automation me use hoti hai.",
                ),
                (
                    "html",
                    "HTML (HyperText Markup Language) web pages ka basic structure banane ke liye istemal hoti hai.",
                ),
                (
                    "sql",
                    "SQL (Structured Query Language) databases me data store, search aur manage karne ki language hai.",
                ),
            ]
            cursor.executemany(
                "INSERT OR IGNORE INTO tech_knowledge (topic, definition) VALUES (?, ?)",
                defaults,
            )
            conn.commit()

        conn.close()

    def search_sqlite_knowledge(self, query):
        words = re.findall(r"\w+", query.lower())
        ignore = {
            "kya",
            "hai",
            "kaun",
            "sa",
            "batao",
            "bata",
            "kisi",
            "ko",
            "bhai",
            "samjha",
        }
        clean_words = [w for w in words if w not in ignore and len(w) > 1]

        if not clean_words:
            return None

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        for word in clean_words:
            cursor.execute(
                "SELECT topic, definition FROM tech_knowledge WHERE LOWER(topic) = ? OR LOWER(topic) LIKE ?",
                (word, f"%{word}%"),
            )
            row = cursor.fetchone()
            if row:
                conn.close()
                return f"🧠 **Knowledge Base ({row[0].upper()}):** {row[1]}"

        conn.close()
        return None

    def get_non_repeating_choice(self, tag, responses):
        if not responses:
            return ""

        if len(responses) == 1:
            return responses[0]

        last_resp = self.last_responses.get(tag)

        available = [r for r in responses if r != last_resp]
        if not available:
            available = responses

        chosen = random.choice(available)
        self.last_responses[tag] = chosen
        return chosen

    def handle_smart_memory_file(self):
        if self.user_name == "pankaj":
            master_file = "ai_memory_pankaj_master.json"
            if os.path.exists(master_file):
                print(
                    f"\n[Access Granted] Welcome back Developer Pankaj! Loading Master File: {master_file}"
                )
            else:
                print(
                    f"\n[Info] Creating Developer Master Brain file: {master_file}"
                )
            return master_file

        if "pankaj" in self.user_name:
            print("\n" + "=" * 65)
            print(
                "❌ ACCESS DENIED: You cannot create a file starting with 'Pankaj'!"
            )
            print("Reason: This is the main developer master file.")
            print("=" * 65 + "\n")
            self.user_name = "guest_user"

        existing_files = glob.glob("ai_memory_*.json")
        user_specific_files = [
            f for f in existing_files if f"_{self.user_name}_" in f
        ]

        if user_specific_files:
            print(
                f"\n[Info] Tumhari purani memory file mil gayi: {user_specific_files[0]}"
            )
            return user_specific_files[0]

        random_id = random.randint(1000, 9999)
        new_file = f"ai_memory_{self.user_name}_{random_id}.json"
        print(f"\n[Info] Nayi memory file ban rahi hai: {new_file}")
        return new_file

    def load_memory(self):
        default_data = [
  {
    "tag": "greeting",
    "patterns": [
      "hi",
      "hello",
      "hey",
      "namaste",
      "oi",
      "hello bhai",
      "kaise ho",
      "kya haal hai",
      "hey bro",
      "wassup",
      "suno",
      "oye",
      "hey bot",
      "yo"
    ],
    "responses": [
      "Arey {name} bhai! Kya scene hai aaj ka? 😎",
      "Oi {name}! Bol bhai, aaj kya naya chal raha hai?",
      "Hey {name}! Kya haal chaal? Kuch spicy khabar hai kya aaj?"
    ],
    "context_responses": {
      "thik": "Badiya bhai! Aur batao aaj kya plan hai?",
      "mast": "Sahi hai bhai, aise hi mast raho! 😎",
      "badhiya": "Ekdam zabardast! Kuch khas chal raha hai kya?"
    }
  },
  {
    "tag": "status_ok",
    "patterns": [
      "theek hu",
      "thik hu",
      "mast hu",
      "badhiya hu",
      "badiya hu",
      "sab sahi hai",
      "ekdam badiya",
      "mast hu bhai",
      "all good",
      "ha sab theek hai",
      "ha sab theek hai tu bata",
      "sab theek hai"
    ],
    "responses": [
      "Sahi hai bawa! Mast raho ekdam! Waise aaj kya special khaya? 🍕",
      "Sunkar badhiya laga {name}! Chal bata fir, aaj din kaisa gaya? 🔥",
      "Badiya bhai! Vaise aaj koi naya kand kiya ya chup chaap baithe ho? 👀"
    ],
    "context_responses": {
      "pizza": "Oo ho! Party hard bhai! Mujhe bhi bhej do thoda 🍕😋",
      "kuch nahi": "Arey waah, simple aur badiya! 😋",
      "bekar": "Arre kya hua bhai? Din bekar kyon gaya?"
    }
  },
  {
    "tag": "acknowledgement",
    "patterns": [
      "ok",
      "okay",
      "k",
      "hmm",
      "accha",
      "achha",
      "sahi hai",
      "got it",
      "samajh gaya",
      "thik hai"
    ],
    "responses": [
      "Set hai bhai! 👍 Aur batao, koi naye gaane sun rahe ho kya aajkal?",
      "Ekdam clear! Waise abhi free ho ya koi kaam nipta rahe ho?",
      "Done bhai! Waise itna chup kyo ho, kuch bolo na! 😁"
    ],
    "context_responses": {
      "free": "Sahi hai fir toh mast chill maaro ya game khelo! 🎮",
      "busy": "Arre kaam nipta lo pehle, main idhar hi hu! 👍",
      "kaam": "Hustle chalu rehna chahiye bhai! ⚡"
    }
  },
  {
    "tag": "courtesy",
    "patterns": [
      "thanks",
      "thank you",
      "shukriya",
      "dhanyawad",
      "thanks bhai",
      "thx",
      "thank u"
    ],
    "responses": [
      "Arre chill karo {name} bhai! Apne hi bande ho. 🙌",
      "Arre welcome bhai! Isme thanks kaisa, party do ab! 🍕",
      "Always active tere liye {name}! Kuch aur chahiye toh bol!"
    ],
    "context_responses": {
      "konsi party": "Samosa party bhai, aur kya! 😋",
      "dilao": "Pehle tum do, fir main dunga! 😜"
    }
  },
  {
    "tag": "goodbye",
    "patterns": [
      "bye",
      "goodbye",
      "chalo bye",
      "see you",
      "alvida",
      "tc",
      "take care",
      "ja raha hu",
      "baad me baat karte hain"
    ],
    "responses": [
      "Chalo {name} bhai! Milte hain break ke baad. 👋",
      "Jao jao, aaram karo! Apna khyal rakhna bhai! 🔥",
      "Tata bhai! Kuch lafda ho toh turant yaad karna!"
    ],
    "context_responses": {
      "sleep": "Good night bro, mast neend lo! 🌙",
      "kal": "Haan kal pakka milte hain! 👋"
    }
  },
  {
    "tag": "agreement_disagreement",
    "patterns": [
      "nahi chahiye",
      "no",
      "na",
      "bilkul nahi"
    ],
    "responses": [
      "Koi nahi bhai, jaisa tera mood! 🤝 Kuch aur baat karein?",
      "Theek hai bhai, no problem. Waise bored toh nahi ho rahe?",
      "Sahi hai! Jab zaroorat lage bol dena, apun idhar hi hai."
    ],
    "context_responses": {}
  },
  {
    "tag": "casual_chitchat",
    "patterns": [
      "kuch nahi",
      "kuchh nahi",
      "kuch nahi chal raha hai",
      "kuchh nahi chal raha hai",
      "nahi soch aise hi baat kar lu",
      "aise hi",
      "bas aise hi",
      "kuch khas nahi",
      "life ma toh kuch nahi ho raha hai",
      "life me kuch nahi ho raha",
      "kuch nahi ho raha"
    ],
    "responses": [
      "Arey aise kaise kuch nahi! Koi mast movie ya series dekhi hogi? 🍿",
      "Bina kisi wajah ke baat karne ka hi alag maza hai! Bol fir kya chal raha hai mind me? ✨",
      "Kuch khas nahi? Arey chill karo fir! Koi accha gaana suggest karu kya?"
    ],
    "context_responses": {
      "ha": "Arijit Singh ka 'Kesariya' ya 'Tum Hi Ho' suno, mood ekdam mast ho jayega! 🎧🎶",
      "kar": "Arijit Singh ka 'Kesariya' ya 'Tum Hi Ho' suno, mood ekdam mast ho jayega! 🎧🎶",
      "yes": "Arijit Singh ka 'Kesariya' ya 'Tum Hi Ho' suno, mood ekdam mast ho jayega! 🎧🎶",
      "na": "Koi baat nahi bhai! Fir kya karne ka plan hai?"
    }
  },
  {
    "tag": "compliment",
    "patterns": [
      "good",
      "nice",
      "great",
      "badiya",
      "bohot achha",
      "mast",
      "oo bahi good",
      "op",
      "superb",
      "awesome"
    ],
    "responses": [
      "Dil jeet liya {name} bhai! ❤️ Aur batao itni tareef ka raaz?",
      "Thanks brother! 🔥 Tu bhi ekdam OP banda hai!",
      "Khushi hui sunkar! Aise hi vibe banaye rakho! 😎"
    ],
    "context_responses": {}
  },
  {
    "tag": "bot_identity",
    "patterns": [
      "tum kon hon",
      "tum kaun ho",
      "who are you",
      "tumhe kisne banaya",
      "who created you",
      "about yourself",
      "tera naam kya hai",
      "tera naam kya",
      "tera naam"
    ],
    "responses": [
      "Main INFINITY-AI hoon! 🤖 Mujhe Pankaj Singh ne Python me scratch se banaya hai. Agar aapko developer ke baare me aur jaanna hai toh unke GitHub pe jaa sakte hain aur unke Discord pe pooch sakte hain sawal ya koi suggestion. Discord ki link unke GitHub profile me hai.\n\nDeveloper GitHub Profile: infinityminds-dev"
    ],
    "context_responses": {}
  },
  {
    "tag": "daily_activity_suggestions",
    "patterns": [
      "chal bata aaj kya karna hai",
      "aaj kya kare",
      "kya kare aaj",
      "aaj kya karna chahiye",
      "bor ho raha hu kya karu",
      "kya karu aaj",
      "bor ho raha hu",
      "kya plan hai ajj ka",
      "kya plan hai aaj ka"
    ],
    "responses": [
      "Arey bawa mast plan banate hain! 🎯 Coding ka mood hai, game khelne ka scene hai, ya chill music sunke aaram karna hai? Kya set karein?"
    ],
    "context_responses": {
      "music": "Mast playlist lagao aur headphone pehen ke chill karo bhai! 🎧🎶",
      "gaana": "Koi apna favourite gaana lagao aur speakers full kar do! 🎶🔊",
      "game": "Kaunsa game khelne ka plan hai? PC game ya mobile game? 🎮🔥",
      "mobile": "Mast BGMI, Free Fire ya Call of Duty lagao aur dosto ke saath machao! 📱💥",
      "pc": "Sahi hai! GTA, Valorant ya Counter-Strike me se kya chalayein? 🖥️🎯",
      "coding": "Sahi hai! Aaj kaunsa naya feature code karne wale ho? 💻⚡",
      "code": "Python me koi naya logic likhe kya aaj? 🐍⚡",
      "walk": "Sahi hai! Thodi taazi hawa lo aur fresh ho ke aao! 🚶‍♂️✨",
      "rest": "Badiya hai bhai! Thodi der aaram karo, mind fresh ho jayega. 🛏️💤",
      "soja": "Aaram se neend poori karo, rest bohot zaroori hai! 😴💤"
    }
  },
  {
    "tag": "music_intent",
    "patterns": [
      "music",
      "music sun lo",
      "gaana sun leta hu",
      "chal music sun leta hu",
      "gaane sunne hain",
      "songs",
      "song sununga"
    ],
    "responses": [
      "Music hi toh asli vibe hai bhai! 🎶 Lofi, Punjabi, ya Rock—aaj kaunsi vibe chalegi?"
    ],
    "context_responses": {
      "punjabi": "Zabardast! High energy Punjabi beats lagao aur mood banao! 🎧🔥",
      "lofi": "Chilled Lofi beats suno, mind ekdam calm ho jayega! ☕🎶",
      "sad": "Arre kya hua bhai? Mood off hai kya jo sad songs sun rahe ho? 💔"
    }
  },
  {
    "tag": "game_intent",
    "patterns": [
      "game khelna hai",
      "mobile game",
      "pc game",
      "game khel lu",
      "chal game khelte hain",
      "gaming"
    ],
    "responses": [
      "Gaming mode ON! 🎮 BGMI, Valorant, ya GTA—aaj kahan machane ka plan hai?"
    ],
    "context_responses": {
      "bgmi": "Arey waah! Chicken Dinner pakka karke aana bhai! 🪖💥",
      "freefire": "Booyah maar ke aao bhai, full rush gameplay! 🎯🔥",
      "valorant": "Clutch marna padega aaj! Headshots ready rakho! 🖥️🎯",
      "gta": "City me ghoomne ka aur tabaahi machane ka plan hai lagta hai! 🚗💥"
    }
  },
  {
    "tag": "tech_coding_fallback",
    "patterns": [
      "python",
      "coding",
      "code",
      "programming",
      "programming language",
      "javascript",
      "html",
      "css",
      "java",
      "c++",
      "bug",
      "error",
      "loop",
      "function",
      "array",
      "database",
      "sql",
      "tech",
      "github",
      "tujha coding ka bare ma kuch pata hai",
      "tumhe coding ke bare me pata hai",
      "coding aati hai kya",
      "coding ke bare me pata hai",
      "loop kya hai",
      "Meri help karga coding ma",
      "Mujhe tujh jaisa AI banana hai kaise banaun",
      "car game ki script",
      "mujhe car game bani hai",
      "mujhe game bani hai",
      "mujhe project bana hai coding se",
      "website bani hai",
      "app bani hai",
      "desktop app bani hai",
      "tech baat karte hain",
      "pc build",
      "android app",
      "new tech",
      "ai news"
    ],
    "responses": [
      "Mujhe abhi coding aur tech ke baare me zyada jankari nahi hai 😅. Iske liye aap ChatGPT ya Gemini jaise Large Language Models (LLM) se pooch sakte hain 🤖. Developer ne abhi mujhe itna develop nahi kiya hai, lekin in future main iska jawab zaroor de paunga!"
    ],
    "context_responses": {
      "python": "Python toh meri core language hai! Developer ne mujhe Python se hi banaya hai 🐍⚡",
      "help": "Main chote moti baatein samajh sakta hu, par heavy programming ke liye ChatGPT best rahega 🤖 ",
      "ai news": "ha bhai ma live news nahi de Sakta hoon kyunki Main Ek offline AI hua main real Time news Nahin De sakta Kisi Bhi chij ki aur na hi main purani news  De sakta hun agar aur kisi chij ke bare mein baat karni hai to main kar sakta hun 🥀"
    }
  },
  {
    "tag": "low_energy_mood",
    "patterns": [
      "maan nahi kar raha hai kuch karne ka",
      "man nahi kar raha hai",
      "kuch karne ka man nahi hai",
      "aaj kuch nahi karna",
      "man nahi hai aaj",
      "aaj mood off hai",
      "thaka hua hu"
    ],
    "responses": [
      "Koi nahi bhai! Kabhi kabhi aaram karna hi best hota hai. Chill maaro, koi zabardasti nahi! 🛌"
    ],
    "context_responses": {
      "kya hua": "Koi tension mat lo bhai, chill karo. Baatein karni ho toh main hu na!",
      "kisi से baat nahi karni": "Koi baat nahi bhai, phone side me rakh kar thodi der aaram kar lo 🛌"
    }
  },
  {
    "tag": "bot_status_query",
    "patterns": [
      "tu bata",
      "tu bata bhai",
      "apna batao",
      "aur batao",
      "kya ho raha hai",
      "tu bata kya kar na hai"
    ],
    "responses": [
      "Main toh chill mode me hu bhai! Tu bata, aaj kya naya chal raha hai life me?",
      "ma toh hamesha ready hai! Tu bol aaj kya tufani karna hai?"
    ],
    "context_responses": {}
  },
  {
    "tag": "custom_2064",
    "patterns": [
      "ooo",
      "oo",
      "oho",
      "wah"
    ],
    "responses": [
      "Full bawaal vibe! 🔥💯"
    ],
    "context_responses": {}
  },
  {
    "tag": "bot_capabilities",
    "patterns": [
      "tu kya kar sakta hai",
      "tum kya kar sakte ho",
      "kya kya kar sakte ho",
      "tum kya kya kar sakte ho",
      "tumhare features kya hain",
      "what can you do",
      "tera kaam kya hai",
      "kya kar sakte ho tum",
      "apne features batao",
      "tujhe kya kya aata hai",
      "tu kya kya samajh sakta hai"
    ],
    "responses": [
      "ma multitalented hu bhai! 🚀\n1. Chill baatein aur mood set karna 😎\n2. Math problems fast solve karna 🧮\n3. Jokes aur advice dena 💡\n4. Teri baatein aur memory yaad rakhna 🧠\n5. PDF files se text read aur extract karna 📄\n6. Images se OCR ke zariye text read karna 🖼️\n\nBol aaj kis cheez me madad chahiye?"
    ],
    "context_responses": {}
  },
  {
    "tag": "bot_current_activity",
    "patterns": [
      "tu kya kar raha hai",
      "tum kya kar rahe ho",
      "kya kar raha hai",
      "kya kar rahe ho"
    ],
    "responses": [
      "Bas {name} bhai, beth ke tere reply ka hi wait kar raha tha! Aur bata kya scene hai?"
    ],
    "context_responses": {}
  },
  {
    "tag": "custom_5567",
    "patterns": [
      "i am back",
      "wapas aa gaya",
      "back"
    ],
    "responses": [
      "Arey bawa aa gaya wapas! 🔥 Chal bata kahan gaye the?"
    ],
    "context_responses": {}
  },
  {
    "tag": "custom_6423",
    "patterns": [
      "good Morning bhai",
      "good morning",
      "good morning bro",
      "gm"
    ],
    "responses": [
      "Good Morning {name}! 🌅 Chai-paani ho gaya? Aaj kya machane wale ho?"
    ],
    "context_responses": {}
  },
  {
    "tag": "custom_1812",
    "patterns": [
      "Good night bhai",
      "good night",
      "good night bro",
      "gn"
    ],
    "responses": [
      "Good Night bhai! 🌙 Phone side me rakho aur mast neend lo!"
    ],
    "context_responses": {}
  },
  {
    "tag": "custom_5087",
    "patterns": [
      "Good evening",
      "good evening bhai",
      "good evening bro",
      "ge"
    ],
    "responses": [
      "Good Evening bhai! 🌆 Sham ka kya plan hai fir?"
    ],
    "context_responses": {}
  },
  {
    "tag": "custom_afternoon",
    "patterns": [
      "good afternoon",
      "good afternoon bhai",
      "afternoon bro"
    ],
    "responses": [
      "Good Afternoon {name} bhai! ☀️ Khana peena ho gaya na?"
    ],
    "context_responses": {}
  },
  {
    "tag": "custom_jokes",
    "patterns": [
      "joke sunao",
      "chutkula sunao",
      "koi joke batao",
      "hassa do bhai",
      "ek aur joke",
      "joke"
    ],
    "responses": [
      "Teacher: 1 se 10 tak ginti sunao!\nStudent: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10!\nTeacher: Shabash! Aage?\nStudent: J, Q, K! 🃏😂",
      "Ek aadmi doctor ke paas gaya: Doctor sahab jab mai chai pita hu to meri aakh me dard hota hai!\nDoctor: Pehle cup me se chammach nikal liya karo! ☕😜",
      "Pappu: Yaar mera mobile pani me gir gaya aur kharab ho gaya.\nFriend: Toh dukandar ko dikhaya?\nPappu: Haan, usne bola isme rice me daal ke rakho.\nFriend: Phir kya hua?\nPappu: Kucch nahi, mobile chawal ke sath pak gaya! 📱🍚",
      "Teacher: Tumne kal homework kyon nahi kiya?\nStudent: Sir, bijli nahi thi.\nTeacher: Toh mombatti jala lete!\nStudent: Sir, maachis nahi thi.\nTeacher: Maachis kyon nahi thi?\nStudent: Pooja ke ghar me rakhi thi.\nTeacher: Toh wahan se le aate!\nStudent: Sir, nahaaya hua nahi tha! 🕯️🤣",
      "Customer: Bhai, is phone me net fast chalta hai kya?\nDukandar: Pata nahi bhai, kal ek banda le gaya tha, aaj tak wapas hi nahi aaya... speed me kahin aage nikal gaya hoga! 🚀📱",
      "Papa: Beta tumhare result ka kya hua?\nBeta: Papa, doctor ka beta doctor bana, engineer ka beta engineer!\nPapa: Aur tum?\nBeta: Main toh mazdoor ka beta hoon na papa, toh fail ho gaya! 👷‍♂️📖",
      "Husband: Aaj khane me kya banaya hai?\nWife: Jo tumne kal bola tha na wahi!\nHusband: Par kal toh maine bola tha ki zahar de do!\nWife: Toh bas wahi bana diya hai, chup chap kha lo! 🍜💀🤣",
      "Santa: Yaar, mera dimaag bohot tez chalta hai!\nBanta: Kaise?\nSanta: Kal train chootne me 2 min bache the, main 1 min pehle hi pahunch gaya! 🏃‍♂️🚂",
      "Boy: Tum itni sundar kaise ho?\nGirl: God ki kripa hai!\nBoy: Lagta hai God ne tum par poori kripa kar di, baaki sab par aalsi ho gaye! 🙄✨",
      "Doctor: Aapko kaunsa rog hai?\nPatient: Doctor sahab, jab bhi kaam karne lagta hoon, neend aane lagti hai!\nDoctor: Ye rog nahi, isse alsi-pan kehte hain! 🛌💤",
      "Pappu: Sir, computer crash ho gaya!\nSir: Re-boot karke dekha?\nPappu: Haan sir, teen baar joota mara par fir bhi nahi chala! 👟💻🤣",
      "Teacher: Dharti ghoomti hai, iska proof kya hai?\nStudent: Sir kal raat ko ghar aaya toh mummy, papa, ghar sab ghoom rahe the! 🌎💫😜",
      "Santa: Yaar, tune Bluetooth se gaana bheja tha, par aaya nahi!\nBanta: Arre bewakoof, raste me red light thi toh ruk gaya hoga! 🛑📱😆",
      "Mom: Beta, TV band kar aur padhne baith!\nSon: Mummy, TV pe toh news aa rahi hai, gyan badh raha hai!\nMom: Aur jo result ke din danda padega usse kya badhega? 📺🧹🤣",
      "Friend: Yaar, tension se kaise bachein?\nPappu: Seedhi baat hai bro, phone flight mode pe dalo aur so jao! ✈️😴💡",
      "Exam Hall me Student:\n'Paper bohot tough aaya hai sir!'\nTeacher: 'Paper nahi beta, tumhari padhai weak hai!'\nStudent: 'Wo toh theek hai sir, par mark toh paper me milte hain, padhai me nahi!' 📝💥😆",
      "Dukandar: Ye kapda bohot waterproof hai!\nCustomer: Achha? Thoda paani daal ke dikhao!\nDukandar: Arre bhai, dukaan me baarish karwaoge kya? 🌧️👕😂",
      "Papa: Tum har waqt phone pe kya karte rehte ho?\nBeta: Papa, future ki planning kar raha hoon!\nPapa: Game me level up karne ko future planning nahi kehte! 🎮🤦‍♂️",
      "Doctor: Aapko subah aur shaam walk karni chahiye!\nPatient: Sir, walk karne se kya hoga?\nDoctor: Pait kam hoga!\nPatient: Lekin sir, mera pait toh pehle se hi peeth se chipka hai! 🚶‍♂️🤣",
      "Teacher: Gravity kya hai?\nStudent: Sir, jab koi cheez aasmaan me jaye aur seedhe aapke sar par gire, toh usse gravity kehte hain! 🍎🤯",
      "Boss: Tum office roz late kyon aate ho?\nEmployee: Sir, raste me ek board laga hai jispe likha hai - 'Aage school hai, dheere chalein!' Isliye main dheere aata hoon! 🚸😂",
      "Pappu: Yaar mujhe ek aisi naukri chahiye jisme kaam kam ho aur salary zyada ho!\nFriend: Ek kaam kar, bank me ATM machine ban ja! 🏧💸😜",
      "Judge: Tumne chor ko chori karte waqt pakda nahi?\nGuard: Sahab, main socha wo apna hi ghar saaf kar raha hoga, mujhe kya pata tha! 🏠💤😂"
    ],
    "context_responses": {
      "aur sunao": "Ek aur suno: Doctor - Tumhare daant me kida kaise laga? Pappu - Mithai khate waqt sir! Doctor - Kida dikha nahi? Pappu - Arre wo mithai me chhup ke baitha tha! 🍬🦷🤣",
      "hahaha": "Haste raho bhai, mood ekdam mast hona chahiye! 😂🔥",
      "bekar": "Arre sorry bhai, agli baar super funny wala sunata hu! 😅"
    }
  },
  {
    "tag": "custom_advice",
    "patterns": [
      "koi advice do",
      "mujhe advice chahiye",
      "kuch salah do",
      "tips do",
      "salah chahiye",
      "study advice",
      "focus kaise kare",
      "life tips"
    ],
    "responses": [
      "Sahi salah chahiye toh simple baat yaad rakho {name} bhai: Ek waqt pe ek hi kaam par focus karo, distraction se door raho aur daily thodi mehnat karo! 🎯",
      "Bhai meri sabse badi advice yehi hai: Consistency banaye rakho! Roz thoda thoda seekhoge toh long run me bohot aage nikal jaoge! 🚀",
      "Agar padhai ya kaam me focus nahi ho raha, toh Pomodoro technique use karo: 25 min kaam + 5 min break! Boht sahi chalta hai! ⏱️💡",
      "Galti karne se mat daro bhai! Har error aur failure ek nayi learning deke jata hai! Bold raho aur aage badho! 🔥",
      "Subah jaldi uthne ki aadat daalo bhai, din me extra time milta hai aur saare kaam aaram se nipat jaate hain! 🌅✨",
      "Social media ka screen time kam karo bhai, asli life screen ke baahar hai jahan real hustle hoti hai! 📵🚀"
    ],
    "context_responses": {
      "thik hai": "Sahi hai bhai, implement karke dekho, zaroor fayda hoga! 🚀",
      "mushkil hai": "Shuru me mushkil lagta hai bhai, par roz thoda thoda try karoge toh aasan ho jayega! 💪"
    }
  },
  {
    "tag": "custom_7212",
    "patterns": [
      "oo new respones",
      "hahahahahhahaha",
      "ya badiya tha",
      "good joke",
      "maza aa gaya",
      "mats joke tha"
    ],
    "responses": [
      "Thank you bhai apki training ki vajah se 🥰🔥",
      "Hehe! Haste raho bhai, mood ekdam fresh rehna chahiye! 😂"
    ],
    "context_responses": {}
  },
  {
    "tag": "custom_3253",
    "patterns": [
      "nachooook",
      "nacho",
      "dance"
    ],
    "responses": [
      "lekin kyo nachooo bhai kya baat hai",
      "Arre waah! Koi badi khushi ki baat hai kya bhai? 🕺🎉"
    ],
    "context_responses": {}
  },
  {
    "tag": "express_frustration",
    "patterns": [
      "aise kon karta hai",
      "aise kaun karta hai",
      "aise kon kar tha hai yaar",
      "kya hai yaar",
      "kya kar raha hai yaar",
      "ye kya baat hui",
      "kya scene hai yaar",
      "pagal hai kya",
      "samajh nahi aa raha"
    ],
    "responses": [
      "Arey sorry {name} bhai! 😅 Dimaag thoda idhar udhar ho gaya tha. Ab bata kya scene hai?",
      "Galti ho gayi bawa! 😂 Aisa nahi karunga ab, tu bata sahi se kya chal raha hai?",
      "Arre gussa mat ho bhai! Robot hu na, kabhi kabhi confuse ho jata hu 😜"
    ],
    "context_responses": {}
  },
  {
    "tag": "user_silent",
    "patterns": [
      "chup hu",
      "shaant hu",
      "kuch nahi bolna",
      "bolna nahi hai",
      "chup rehna hai",
      "shant hu"
    ],
    "responses": [
      "Arey itna chup kyo ho {name} bhai? Subah se koi kand kar diya kya? 👀",
      "Shanti bhi zaroori hai bawa, par mujhse kya chupa raha hai? Bol de! 😁",
      "Koi nahi bhai, aaram se baitho. Jab bolne ka mann kare batana! ☕"
    ],
    "context_responses": {}
  },
  {
    "tag": "user_sad_cry",
    "patterns": [
      "ro raha hu",
      "dukh hai",
      "duokhi hu",
      "sad hu",
      "mood kharab hai",
      "dil toot gaya",
      "rula mat"
    ],
    "responses": [
      "Arey kya hua {name} bhai? Rona mat, kisne pareshan kiya batayo mujhe! 😠",
      "Bhai tension mat le, sab theek ho jayega. Kuch hua hai kya?",
      "Chill maaro bhai! Ek baar lambi saans lo aur batao kya tension hai? 🫂"
    ],
    "context_responses": {
      "breakup": "Arey bhai, dil mat chota karo! Life me aage bohot accha likha hai! 💪",
      "padhai": "Tension mat lo bhai, break lo aur thodi der baad aaram se padhna! 📚",
      "ghar": "Sab sorted ho jayega bhai, calm raho thoda! ☕"
    }
  },
  {
    "tag": "bot_confusion",
    "patterns": [
      "samajh nahi aaya",
      "kya bola",
      "pata nahi",
      "kya keh raha hai",
      "samajh nahi tha"
    ],
    "responses": [
      "Arre lagta hai mera circuit thoda hil gaya! Phir se batao simple me 😅",
      "Arey sorry {name} bhai, thoda confuse ho gaya tha. Phir se bolo!"
    ],
    "context_responses": {}
  },
  {
    "tag": "weather_inquiry",
    "patterns": [
      "mausam kaisa hai",
      "aaj baarish hogi kya",
      "dhoop hai kya",
      "garmi hai"
    ],
    "responses": [
      "Mausam ka toh pata nahi bhai, par tu ghar pe baith ke chill maar! ☀️🌧️"
    ],
    "context_responses": {
      "garmi": "Thanda paani piyo aur AC/fan me baitho bhai! 🧊",
      "baarish": "Chai pakode ka scene banao fir toh! ☕🌧️"
    }
  },
  {
    "tag": "bad_day_feeling",
    "patterns": [
      "acha nahi tha",
      "achha nahi tha",
      "bura tha",
      "kuch khas nahi gaya",
      "din acha nahi tha",
      "din kharab tha",
      "bekar tha",
      "bekar gaya",
      "accha nahi gaya"
    ],
    "responses": [
      "Arey kya hua {name}? Din me aisa kya ho gaya? 😔 Aaja dil halka kar!",
      "Oh ho! Kya tension ho gayi bhai? Koi lafda hua kya aaj?",
      "Koi nahi bhai, har din ek jaisa nahi hota. Thoda aaram karo aur chill maaro! ☕"
    ],
    "context_responses": {}
  },
  {
    "tag": "clarification_correction",
    "patterns": [
      "din ki  kar raha hu",
      "teri baat nahi kar raha",
      "are bhai din ki baat kar raha hu teri nahi",
      "tujhe nahi bol raha",
      "dhyan se sun"
    ],
    "responses": [
      "Acha acha!  {name} My bad , main galat samajh gaya tha 😅 Haan toh bata, din me kya gadbad hui?",
      "Sahi pakde hain! Main thoda confuse ho gaya tha. Haan bata kya hua tha aaj?"
    ],
    "context_responses": {}
  },
  {
    "tag": "custom_6480",
    "patterns": [
      "minecraft"
    ],
    "responses": [
      "Oo bhai phri toh next level kam hoga toh kya socha hai koi building Bani hai ya minecraft with create mod Khel na hai 😋"
    ],
    "context_responses": {}
  },
  {
    "tag": "food_hungry",
    "patterns": [
      "bhookh lagi hai",
      "khana khana hai",
      "kya khau",
      "kuch khane ka man hai",
      "khana peena"
    ],
    "responses": [
      "Arey pehle pet pooja, fir kaam dooja! 🍕 Burgers, Momos ya mast ghar ka khana?"
    ],
    "context_responses": {
      "momos": "Teekhi chutney ke sath momos ka alag hi swad hai! 🥟🔥",
      "burger": "Extra cheese burger manga lo fir toh! 🍔"
    }
  }
]

        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.memory_db = (
                        data if isinstance(data, list) else default_data
                    )
            except Exception:
                self.memory_db = default_data
        else:
            self.memory_db = default_data
            self.save_memory()

        self.classifier.train(self.memory_db)

    def clean_text_for_json(self, text):
        if not isinstance(text, str):
            return text
        return text.strip()

    def save_memory(self):
        cleaned_db = []
        if isinstance(self.memory_db, list):
            for item in self.memory_db:
                if not isinstance(item, dict):
                    continue

                if (
                    "full_text" in item
                    or item.get("source", "").endswith(".pdf")
                    or "image" in item.get("pattern", "")
                ):
                    continue

                clean_patterns = [
                    self.clean_text_for_json(p)
                    for p in item.get("patterns", [])
                    if self.clean_text_for_json(p)
                ]
                clean_responses = [
                    self.clean_text_for_json(r)
                    for r in item.get("responses", [])
                    if self.clean_text_for_json(r)
                ]

                if clean_patterns and clean_responses:
                    cleaned_db.append(
                        {
                            "tag": item.get("tag", "general"),
                            "patterns": clean_patterns,
                            "responses": clean_responses,
                            "context_responses": item.get(
                                "context_responses", {}
                            ),
                        }
                    )

        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(cleaned_db, f, indent=2, ensure_ascii=False)

        self.classifier.train(self.memory_db)

    def generate_proactive_greeting(self):
        greetings = [
            f"Hey {self.user_name.capitalize()}! Main ready hoon, aaj kya chal raha hai? 😎",
            f"Oi {self.user_name.capitalize()}! Welcome back. Batao aaj kya plan hai? 🚀",
            f"Yo {self.user_name.capitalize()}! INFINITY-AI online hai, kaise ho aaj? 🔥",
        ]
        return random.choice(greetings)

    def learn_new_response(self, user_query, correct_response):
        query_clean = self.clean_text_for_json(user_query.lower())
        response_clean = self.clean_text_for_json(correct_response)

        if not query_clean or not response_clean:
            return

        learned = False
        for item in self.memory_db:
            if isinstance(item, dict) and "patterns" in item:
                if query_clean in [p.lower() for p in item["patterns"]]:
                    if "responses" in item:
                        if response_clean not in item["responses"]:
                            item["responses"].append(response_clean)
                        learned = True
                        break

        if not learned:
            self.memory_db.append(
                {
                    "tag": f"custom_{random.randint(1000, 9999)}",
                    "patterns": [query_clean],
                    "responses": [response_clean],
                    "context_responses": {},
                }
            )

        self.save_memory()

    def get_current_time_slot(self):
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 22:
            return "evening"
        else:
            return "night"

    def check_time_greeting_correction(self, text_lower):
        current_slot = self.get_current_time_slot()

        greetings_map = {
            "morning": ["good morning", "gm", "morning"],
            "afternoon": ["good afternoon", "afternoon"],
            "evening": ["good evening", "ge", "evening"],
            "night": ["good night", "gn", "night"],
        }

        hindi_slot_names = {
            "morning": "Morning/Subah",
            "afternoon": "Afternoon/Dopahar",
            "evening": "Evening/Shaam",
            "night": "Night/Raat",
        }

        detected_slot = None
        for slot, keywords in greetings_map.items():
            if any(k in text_lower for k in keywords):
                detected_slot = slot
                break

        if detected_slot and detected_slot != current_slot:
            actual = hindi_slot_names[current_slot]
            return f"Arre {self.user_name.capitalize()} bhai, abhi {actual} ho raha hai! Pehle ghadi toh dekh lo 😜"

        return None

    def handle_date_time_utilities(self, text_lower):
        now = datetime.now()

        if "kal" in text_lower:
            if "pehle" in text_lower or "beeta" in text_lower:
                target = now - timedelta(days=1)
                return f"📅 **Past Date Info:** Kal **{target.strftime('%A')}** thi ({target.strftime('%d %B %Y')})."
            else:
                target = now + timedelta(days=1)
                return f"📅 **Future Date Info:** Kal **{target.strftime('%A')}** hoga ({target.strftime('%d %B %Y')})."

        if "parso" in text_lower:
            if "pehle" in text_lower or "beeta" in text_lower:
                target = now - timedelta(days=2)
                return f"📅 **Past Date Info:** Parso **{target.strftime('%A')}** thi ({target.strftime('%d %B %Y')})."
            else:
                target = now + timedelta(days=2)
                return f"📅 **Future Date Info:** Parso **{target.strftime('%A')}** hoga ({target.strftime('%d %B %Y')})."

        # FIXED REGEX: Matches 'baad', 'bad', and typo 'bada' along with 'pehle'
        match_days = re.search(r"(\d+)\s*din\s*(baad|bad|bada|pehle)", text_lower)
        if match_days:
            days = int(match_days.group(1))
            mode = match_days.group(2)

            if mode == "pehle":
                target_date = now - timedelta(days=days)
                return f"🗓️ **Past Date:** {days} din pehle **{target_date.strftime('%d %B %Y (%A)')}** thi."
            else:
                target_date = now + timedelta(days=days)
                return f"🗓️ **Future Date:** {days} din baad **{target_date.strftime('%d %B %Y (%A)')}** hogi."

        if any(
            k in text_lower
            for k in ["aaj ka din", "aaj din", "kaunsa din", "what day"]
        ):
            return f"📅 **Date & Day Info:** Aaj **{now.strftime('%A')}** hai ({now.strftime('%d %B %Y')})."

        if any(
            k in text_lower for k in ["aaj date", "aaj ki date", "today date", "ajj ka din"]
        ):
            return f"📅 **Current Date:** {now.strftime('%d-%m-%Y')} ({now.strftime('%A')})"

        if any(
            k in text_lower
            for k in ["time kya hua", "kitne baje", "current time"]
        ):
            return f"⏰ **Current Time:** {now.strftime('%I:%M %p')}"

        return None


    def handle_converters(self, text_lower):
        match = re.search(
            r"(\d+\.?\d*)\s*([a-zA-Z]+)\s*(?:to|in)?\s*([a-zA-Z]+)", text_lower
        )
        if not match:
            return None

        val = float(match.group(1))
        unit_from = match.group(2).lower()
        unit_to = match.group(3).lower()

        length_factors = {
            "cm": 0.01,
            "centimeter": 0.01,
            "centimeters": 0.01,
            "m": 1.0,
            "meter": 1.0,
            "meters": 1.0,
            "km": 1000.0,
            "kilometer": 1000.0,
            "kilometers": 1000.0,
            "feet": 0.3048,
            "foot": 0.3048,
            "ft": 0.3048,
            "inch": 0.0254,
            "inches": 0.0254,
            "in": 0.0254,
            "mile": 1609.34,
            "miles": 1609.34,
            "yard": 0.9144,
            "yards": 0.9144,
        }

        weight_factors = {
            "g": 1.0,
            "gram": 1.0,
            "grams": 1.0,
            "kg": 1000.0,
            "kilogram": 1000.0,
            "kilograms": 1000.0,
            "mg": 0.001,
            "milligram": 0.001,
            "lb": 453.592,
            "lbs": 453.592,
            "pound": 453.592,
            "pounds": 453.592,
        }

        data_factors = {
            "kb": 1 / 1024,
            "mb": 1.0,
            "gb": 1024.0,
            "tb": 1024 * 1024.0,
        }

        # Converter output display fix (Clean Number format)
        if unit_from in length_factors and unit_to in length_factors:
            base_val = val * length_factors[unit_from]
            res = base_val / length_factors[unit_to]
            res_str = f"{res:,.0f}" if res.is_integer() else f"{res:,.2f}"
            return f"📏 **Unit Converter:** {val} {unit_from} = **{res_str} {unit_to}**"

        if unit_from in weight_factors and unit_to in weight_factors:
            base_val = val * weight_factors[unit_from]
            res = base_val / weight_factors[unit_to]
            res_str = f"{res:,.0f}" if res.is_integer() else f"{res:,.2f}"
            return f"⚖️ **Weight Converter:** {val} {unit_from} = **{res_str} {unit_to}**"

        if unit_from in data_factors and unit_to in data_factors:
            base_val = val * data_factors[unit_from]
            res = base_val / data_factors[unit_to]
            res_str = f"{res:,.0f}" if res.is_integer() else f"{res:,.2f}"
            return f"💾 **Storage Converter:** {val} {unit_from} = **{res_str} {unit_to}**"

        return None

    def summarize_text(self, text, max_sentences=2):
        sentences = [
            s.strip() for s in re.split(r"[.!?\n]", text) if s.strip()
        ]
        if len(sentences) <= max_sentences:
            return text

        words = re.findall(r"\w+", text.lower())
        stop_words = {
            "is",
            "the",
            "a",
            "an",
            "and",
            "or",
            "to",
            "in",
            "of",
            "for",
            "on",
            "with",
            "this",
            "that",
            "hai",
            "ko",
            "ki",
            "se",
        }
        filtered_words = [
            w for w in words if w not in stop_words and len(w) > 2
        ]

        if not filtered_words:
            return ". ".join(sentences[:max_sentences]) + "."

        word_freq = Counter(filtered_words)

        sentence_scores = {}
        for idx, sentence in enumerate(sentences):
            score = 0
            for word in re.findall(r"\w+", sentence.lower()):
                if word in word_freq:
                    score += word_freq[word]
            sentence_scores[idx] = score

        ranked = sorted(
            sentence_scores.items(), key=lambda x: x[1], reverse=True
        )
        top_indices = sorted([r[0] for r in ranked[:max_sentences]])

        summary = " ".join([sentences[i] for i in top_indices])
        return f"📝 **Offline Text Summary:**\n{summary}"

    def check_dynamic_advice(self, text_lower):
        mood_triggers = {
            "bored": ["bore", "boring", "paka", "kuch nahi kar raha"],
            "tired": ["thak", "tired", "sleepy", "neend"],
            "stressed": ["stress", "tension", "pareshan", "headache"],
        }

        detected_mood = None
        for mood, keys in mood_triggers.items():
            if any(k in text_lower for k in keys):
                detected_mood = mood
                break

        if detected_mood == "bored":
            advice_list = [
                f"{self.user_name.capitalize()} bhai, thodi der fav playlist chala ke dance kar le ya game khel le! 🎧🎮",
                f"Bore ho rahe ho toh 15-min ki walk le aao ya koi joke suno! 🚶‍♂️🤣",
            ]
            return random.choice(advice_list)

        elif detected_mood == "tired":
            advice_list = [
                f"{self.user_name.capitalize()} bhai, screen off karo aur 20-min ka power nap le lo! 😴🛌",
                "Thoda thanda paani piyo aur stretch kar lo, energy wapas aayegi! 🥤✨",
            ]
            return random.choice(advice_list)

        elif detected_mood == "stressed":
            advice_list = [
                "Bhai bilkul tension mat lo. Lambi saans lo aur 10 min coding se break le lo! 🧘‍♂️✨",
                "Stress lene se kuch nahi hoga, thoda relaxed music suno aur chai/coffee piyo! ☕🎧",
            ]
            return random.choice(advice_list)

        return None

    def solve_math(self, text):
        clean_text = (
            text.lower().replace("x", "*").replace("=", "").replace("^", "**")
        )

        safe_dict = {
            "sqrt": math.sqrt,
            "sin": lambda x: round(math.sin(math.radians(x)), 4),
            "cos": lambda x: round(math.cos(math.radians(x)), 4),
            "tan": lambda x: round(math.tan(math.radians(x)), 4),
            "fact": math.factorial,
            "abs": abs,
            "pi": math.pi,
            "e": math.e,
        }

        match = re.search(
            r"(?:[a-z]+\([^)]+\)|[\d\.\s\+\-\*\/\(\)\^\,]+)+", clean_text
        )
        if match:
            expr = match.group().strip()
            expr = re.sub(r"[\+\-\*\/]+$", "", expr).strip()

            has_op = any(op in expr for op in ["+", "-", "*", "/", "**"])
            has_func = any(fn in expr for fn in safe_dict.keys())

            if (has_op or has_func) and len(expr) > 1:
                try:
                    res = eval(expr, {"__builtins__": None}, safe_dict)
                    if isinstance(res, float) and res.is_integer():
                        res = int(res)
                    return f"Math: {expr} = {res}"
                except Exception:
                    return None
        return None

    def get_full_session_history_reply(self, text):
        text_lower = text.lower()
        if any(
            k in text_lower
            for k in [
                "sawal",
                "history",
                "pehle",
                "pehla",
                "phele",
                "question",
            ]
        ):
            user_queries = [
                h["content"]
                for h in self.session_history
                if h["role"] == "user"
            ]
            if len(user_queries) <= 1:
                return "Abhi tak session me aur koi purana sawal nahi hai!"

            past_all = [
                f"{i+1}. {q}" for i, q in enumerate(user_queries[:-1])
            ]
            return "Poori Session History -> " + " | ".join(past_all)
        return None

    def find_fuzzy_match(self, input_text, cutoff=0.55):
        best_match_item = None
        highest_ratio = 0.0

        for item in self.memory_db:
            if not isinstance(item, dict):
                continue
            for pattern in item.get("patterns", []):
                ratio = difflib.SequenceMatcher(
                    None, input_text.lower(), pattern.lower()
                ).ratio()
                if ratio > highest_ratio:
                    highest_ratio = ratio
                    best_match_item = item

        if highest_ratio >= cutoff:
            return best_match_item, highest_ratio
        return None, 0.0

    def check_context_reply(self, text_lower):
        if not self.current_context:
            return None

        for item in self.memory_db:
            if (
                isinstance(item, dict)
                and item.get("tag") == self.current_context
            ):
                ctx_responses = item.get("context_responses", {})
                for key, resp in ctx_responses.items():
                    if key in text_lower:
                        self.current_context = None
                        return resp.replace("{name}", self.user_name)
        return None

    def format_extracted_content(
        self, raw_text, source_name, content_type="Image"
    ):
        clean_lines = [
            line.strip() for line in raw_text.splitlines() if line.strip()
        ]
        if not clean_lines:
            return f"🖼️ **{content_type} Scan ({source_name}):** Is file me koi text nahi mil saka."

        total_words = len(raw_text.split())

        explanation = (
            f"📋 **{content_type} Analysis & Summary ({source_name})**\n"
        )
        explanation += f"• **Total Words Detected:** {total_words}\n"
        explanation += f"• **Total Lines Extracted:** {len(clean_lines)}\n\n"
        explanation += "💡 **Point-wise Breakdown (Extracted Content):**\n\n"

        for idx, line in enumerate(clean_lines, 1):
            explanation += f"  {idx}. {line}\n"

        return explanation

    def check_latest_media_memory_reply(self, text_lower):
        if not isinstance(self.memory_db, list):
            return None

        for item in reversed(self.memory_db):
            if not isinstance(item, dict):
                continue

            tag = item.get("tag", "")
            source = item.get("source", "").lower()

            is_image = tag == "image_context" or source.endswith(
                (".png", ".jpg", ".jpeg", ".webp")
            )
            is_pdf = tag == "pdf_context" or source.endswith(".pdf")

            if (is_image or is_pdf) and "full_text" in item:
                file_text = item.get("full_text", "")
                source_name = item.get("source", "Uploaded File")
                content_type = "Image" if is_image else "PDF Document"

                if any(
                    k in text_lower
                    for k in [
                        "summary",
                        "short karo",
                        "chota karo",
                        "chota karke batao",
                    ]
                ):
                    return (
                        f"📄 **Summary for {source_name}:**\n"
                        + self.summarize_text(file_text)
                    )

                if is_image and any(
                    k in text_lower
                    for k in [
                        "total",
                        "sum",
                        "hisab",
                        "amount",
                        "fees",
                        "kitna",
                    ]
                ):
                    found_nums = re.findall(r"\b\d[\d,]*\b", file_text)
                    clean_nums = []
                    for n in found_nums:
                        val = int(n.replace(",", ""))
                        if val > 0:
                            clean_nums.append(val)

                    if clean_nums:
                        total_val = sum(clean_nums)
                        num_str = " + ".join([f"{v:,}" for v in clean_nums])
                        return f"🖼️ **Image Total Calculation ({source_name}):**\n\n• **Detected Numbers:** {num_str}\n• **Total Amount:** {total_val:,}"

                explain_keywords = [
                    "explain",
                    "samjha",
                    "samjhao",
                    "detail",
                    "kya keh raha hai",
                    "matlab",
                    "summary",
                    "kya hai",
                    "scan",
                    "image",
                    "photo",
                    "pic",
                    "ocr",
                    "likha",
                    "isme",
                    "batao",
                    "bata",
                    "pdf",
                    "document",
                ]
                if any(k in text_lower for k in explain_keywords):
                    return self.format_extracted_content(
                        file_text, source_name, content_type
                    )

                words = [
                    w for w in re.findall(r"\w+", text_lower) if len(w) > 3
                ]
                for w in words:
                    if w in file_text.lower():
                        pos = file_text.lower().find(w)
                        start = max(0, pos - 50)
                        end = min(len(file_text), pos + 250)
                        snippet = (
                            file_text[start:end].replace("\n", " ").strip()
                        )
                        icon = "🖼️" if is_image else "📄"
                        return f"{icon} **Context Match from {source_name}**\n\n...{snippet}..."

                break

        return None

    def process_single_query(self, sub_query):
        sub_text = sub_query.strip()
        if not sub_text:
            return None

        text_lower = sub_text.lower()

        time_corrected = self.check_time_greeting_correction(text_lower)
        if time_corrected:
            return time_corrected

        date_time_utility = self.handle_date_time_utilities(text_lower)
        if date_time_utility:
            return date_time_utility

        converter_ans = self.handle_converters(text_lower)
        if converter_ans:
            return converter_ans

        if any(
            k in text_lower for k in ["summarize", "summary", "chota karo"]
        ) and len(sub_text.split()) > 10:
            return self.summarize_text(sub_text)

        advice = self.check_dynamic_advice(text_lower)
        if advice:
            return advice

        math_ans = self.solve_math(sub_text)
        if math_ans:
            return math_ans

        # SQLite Search
        sqlite_ans = self.search_sqlite_knowledge(sub_text)
        if sqlite_ans:
            return sqlite_ans

        # Media Context
        media_reply = self.check_latest_media_memory_reply(text_lower)
        if media_reply:
            return media_reply

        hist_ans = self.get_full_session_history_reply(sub_text)
        if hist_ans:
            return hist_ans

        ctx_reply = self.check_context_reply(text_lower)
        if ctx_reply:
            return ctx_reply

        for item in self.memory_db:
            if isinstance(item, dict) and "patterns" in item:
                if text_lower in [p.lower() for p in item["patterns"]]:
                    if "responses" in item and item["responses"]:
                        self.current_context = item.get("tag")
                        chosen = self.get_non_repeating_choice(
                            item.get("tag"), item["responses"]
                        )
                        return chosen.replace("{name}", self.user_name)

        predicted_tag, score = self.classifier.predict_intent(
            text_lower, threshold=0.20
        )
        if predicted_tag:
            for item in self.memory_db:
                if (
                    isinstance(item, dict)
                    and item.get("tag") == predicted_tag
                    and item.get("responses")
                ):
                    self.current_context = predicted_tag
                    chosen = self.get_non_repeating_choice(
                        predicted_tag, item["responses"]
                    )
                    return chosen.replace("{name}", self.user_name)

        fuzzy_item, similarity = self.find_fuzzy_match(text_lower, cutoff=0.55)
        if (
            fuzzy_item
            and isinstance(fuzzy_item, dict)
            and "responses" in fuzzy_item
        ):
            tag = fuzzy_item.get("tag")
            self.current_context = tag
            chosen = self.get_non_repeating_choice(
                tag, fuzzy_item["responses"]
            )
            return chosen.replace("{name}", self.user_name)

        return None

    def respond(self, user_input):
        raw_text = user_input.strip()
        if not raw_text:
            return "Kuch bologe tabhi toh jawab doonga! 😉"

        if self.last_unknown_query is not None:
            prompt_query = self.last_unknown_query
            self.last_unknown_query = None
            self.learn_new_response(prompt_query, raw_text)
            return f"Got it {self.user_name}! Seekh gaya. Ab se '{prompt_query}' par yahi jawab doonga! 😎👌"

        self.session_history.append({"role": "user", "content": raw_text})

        math_pattern = r"(\d+[\+\-\*\/\^]+\d+[\+\-\*\/\d]*)"
        prepared_text = re.sub(math_pattern, r" , \1 , ", raw_text)

        parts = re.split(r",|\.|\?|\s+aur\s+|\s+or\s+", prepared_text)

        if len([p for p in parts if p.strip()]) == 1:
            ans = self.process_single_query(raw_text)
            if ans:
                return ans

        responses = []
        unknown_part = None

        for part in parts:
            part_str = part.strip()
            if not part_str:
                continue

            ans = self.process_single_query(part_str)
            if ans:
                if ans not in responses:
                    responses.append(ans)
            else:
                if len(part_str) > 2 and not part_str.isdigit():
                    unknown_part = part_str

        if responses:
            if len(responses) == 1:
                return responses[0]
            else:
                formatted_resp = "\n" + "\n".join(
                    [f"• {r}" for r in responses]
                )
                return formatted_resp

        if unknown_part:
            self.last_unknown_query = unknown_part
            return f"Mujhe iska matlab nahi pata '{unknown_part}' ({self.user_name}). Jab main ye suno, toh kya jawab doon? 🤔"

        self.last_unknown_query = raw_text
        return f"Mujhe iska matlab nahi pata {self.user_name}. Jab main '{raw_text}' suno, toh kya jawab doon? 🤔"


if __name__ == "__main__":
    user_name = input("Enter your name: ").strip() or "Guest"
    ai = MainAIEngine(user_name=user_name)

    print("\n========================================================")
    print(
        f"  FINAL ENGINE V5.6 SQLITE & UTILITY INTEGRATED | File:"
        f" {ai.memory_file}"
    )
    print("========================================================\n")

    print(f"AI: {ai.generate_proactive_greeting()}\n")

    while True:
        try:
            user_input = input(f"{ai.user_name}: ").strip()
            if user_input.lower() in ["exit", "quit"]:
                print(
                    f"Session Ended. Permanent Brain saved in {ai.memory_file}!"
                )
                break

            response = ai.respond(user_input)
            print(f"AI: {response}\n")

        except (EOFError, KeyboardInterrupt):
            break
