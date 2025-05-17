from flask import Flask, render_template, request, jsonify, send_from_directory
from langdetect import detect, LangDetectException
from datetime import datetime
import os
import speech_recognition as sr
import tempfile
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

class ByDroid:
    def __init__(self):
        self.name = "ByDroid1.0"
        self.company = "sasaki-compagnie"
        self.support = "Smart compagnie"
        self.creators = ["Équipe Technique sasaki-compagnie", "Soutenu par Smart compagnie"]
        self.version = "1.0"
        self.recognizer = sr.Recognizer()

    def get_response(self, query, lang="fr"):
        try:
            if not lang:
                lang = detect(query)
        except LangDetectException:
            lang = "en"

        solutions = {
            "network": {
                "fr": "Problème réseau ? Redémarrez le routeur, vérifiez les câbles et assurez-vous que le Wi-Fi est activé.",
                "en": "Network issue? Reboot your router, check cables and make sure Wi-Fi is enabled."
            },
            "time": {
                "fr": f"Il est {datetime.now().strftime('%H:%M')} (heure système). Date: {datetime.now().strftime('%d/%m/%Y')}",
                "en": f"It's {datetime.now().strftime('%H:%M')} (system time). Date: {datetime.now().strftime('%m/%d/%Y')}"
            },
            "hardware": {
                "fr": "Pour les problèmes matériels, vérifiez les connexions, redémarrez l'appareil et mettez à jour les pilotes.",
                "en": "For hardware issues, check connections, reboot the device and update drivers."
            },
            "software": {
                "fr": "Problème logiciel ? Essayez de réinstaller le programme ou de le mettre à jour vers la dernière version.",
                "en": "Software issue? Try reinstalling the program or updating to the latest version."
            },
            "virus": {
                "fr": "Suspicion de virus ? Lancez une analyse complète avec votre antivirus et mettez-le à jour.",
                "en": "Virus suspicion? Run a full scan with your antivirus and update it."
            },
            "performance": {
                "fr": "Pour améliorer les performances, fermez les programmes inutiles, nettoyez le disque et ajoutez de la RAM.",
                "en": "To improve performance, close unnecessary programs, clean the disk and add more RAM."
            },
            "default": {
                "fr": "Je n'ai pas de solution précise. Contactez le support sasaki-compagnie avec les détails de votre problème.",
                "en": "I don't have a specific solution. Contact sasaki-compagnie support with details of your issue."
            }
        }

        query_lower = query.lower()
        
        if "réseau" in query_lower or "network" in query_lower or "wifi" in query_lower or "internet" in query_lower:
            return solutions["network"].get(lang, solutions["network"]["en"])
        elif "heure" in query_lower or "time" in query_lower or "date" in query_lower:
            return solutions["time"].get(lang, solutions["time"]["en"])
        elif "matériel" in query_lower or "hardware" in query_lower or "écran" in query_lower or "screen" in query_lower or "clavier" in query_lower or "keyboard" in query_lower:
            return solutions["hardware"].get(lang, solutions["hardware"]["en"])
        elif "logiciel" in query_lower or "software" in query_lower or "programme" in query_lower or "application" in query_lower:
            return solutions["software"].get(lang, solutions["software"]["en"])
        elif "virus" in query_lower or "malware" in query_lower or "antivirus" in query_lower:
            return solutions["virus"].get(lang, solutions["virus"]["en"])
        elif "lent" in query_lower or "performance" in query_lower or "rapide" in query_lower or "speed" in query_lower:
            return solutions["performance"].get(lang, solutions["performance"]["en"])
        else:
            return solutions["default"].get(lang, solutions["default"]["en"])

    def process_audio(self, audio_path, lang="fr"):
        try:
            with sr.AudioFile(audio_path) as source:
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data, language=lang)
                return text, None
        except Exception as e:
            return None, str(e)

@app.route("/")
def home():
    bot = ByDroid()
    now = datetime.now()
    return render_template("index.html", 
                         bot_name=bot.name,
                         company=bot.company,
                         support=bot.support,
                         creators=bot.creators,
                         version=bot.version,
                         now=now)

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    query = data.get("query", "")
    lang = data.get("lang", "fr")
    
    bot = ByDroid()
    response = bot.get_response(query, lang)
    
    return jsonify({
        "response": response,
        "creators": bot.creators
    })

@app.route("/upload_audio", methods=["POST"])
def upload_audio():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
    
    audio_file = request.files['audio']
    lang = request.form.get('lang', 'fr')
    
    if audio_file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    unique_id = str(uuid.uuid4())
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"audio_{unique_id}.wav")
    audio_file.save(temp_path)
    
    bot = ByDroid()
    text, error = bot.process_audio(temp_path, lang)
    
    try:
        os.remove(temp_path)
    except:
        pass
    
    if error:
        return jsonify({"error": error}), 500
    
    response = bot.get_response(text, lang)
    
    return jsonify({
        "text": text,
        "response": response
    })

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == "__main__":
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)