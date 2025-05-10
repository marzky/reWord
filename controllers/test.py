import random
import time
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from core.files import Files

class Test():
    def __init__(self, parent):
        self.parent = parent
        self.layout = parent.findChild(QtWidgets.QVBoxLayout, "testLayout")
        self.question = []
        self.current_index = 0
        self.correct_count = 0
        self.total_time = 0
        self.time_per_question = []
        self.question_start_time = None

    def reset_state(self):
        self.questions = []
        self.current_index = 0
        self.correct_count = 0
        self.total_time = 0
        self.time_per_question = []
        self.question_start_time = None

    def start(self, title):
        self.reset_state()
        self.title = title
        data = Files.read(title)
        words = data.get("words", [])
        if len(words) < 4:
            QtWidgets.QMessageBox.warning(self.parent, "Not enough data", "At least 4 words are required for the test.")
            return
        self.questions = self.generate_questions(words)
        self.parent.pages.setCurrentWidget(self.parent.testView)
        self.show_question()

    def start_with_words(self, words):
        self.reset_state()
        self.source_words = words
        if len(words) < 4:
            QtWidgets.QMessageBox.warning(self.parent, "Not enough data", "At least 4 words are required for the test.")
            return
        self.questions = self.generate_questions(words)
        self.parent.pages.setCurrentWidget(self.parent.testView)
        self.show_question()

    def generate_questions(self, words):
        random.shuffle(words)
        questions = []
        for word_data in words:
            correct = word_data["translation"]
            word = word_data["word"]
            wrong_choices = [w["translation"] for w in random.sample(words, min(len(words), 10)) if w["translation"] != correct]
            choices = [correct] + wrong_choices[:3]
            random.shuffle(choices)
            questions.append({"word": word, "correct": correct, "choices": choices})
        return questions

    def show_question(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
            else:
                del item

        if self.current_index >= len(self.questions):
            self.show_results()
            return

        self.question_start_time = time.monotonic()
        q = self.questions[self.current_index]

        count_lbl = QtWidgets.QLabel(f"{self.current_index + 1} / {len(self.questions)}", alignment=Qt.AlignHCenter | Qt.AlignTop)
        count_lbl.setStyleSheet("font: 20px 'Funnel Sans Light'; color: white;")
        self.layout.addWidget(count_lbl)
        self.layout.addStretch()

        lbl = QtWidgets.QLabel(f"{self.current_index + 1}. {q['word']}")
        lbl.setStyleSheet("font: 20px; color: white;")
        lbl.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(lbl)
        self.layout.addStretch()

        q_number = 1
        for choice in q["choices"]:
            btn = QtWidgets.QPushButton(f"{q_number}. {choice}")
            q_number += 1
            btn.setStyleSheet("""QPushButton{
                    background-color: #1B1B1B;
                    border-radius: 7px;
                    color: white;
                    font: 20px "Funnel Sans";
                    }

                    QPushButton::hover{
                    background-color: #2D2D2D;
                    }

                    QPushButton::pressed{
                    background-color: #1B1B1B;
                    }""")
            btn.setFixedHeight(35)
            btn.clicked.connect(lambda _, c=choice: self.check_answer(c))
            self.layout.addWidget(btn)

    def check_answer(self, selected):
        elapsed = time.monotonic() - self.question_start_time
        self.total_time += elapsed
        self.time_per_question.append(elapsed)

        correct = self.questions[self.current_index]["correct"]
        if selected == correct:
            self.correct_count += 1

        self.current_index += 1
        self.show_question()

    def show_results(self):
        for i in reversed(range(self.layout.count())):
            item = self.layout.itemAt(i)
            if widget := item.widget():
                widget.setParent(None)

        total_q = len(self.questions)
        accuracy = self.correct_count / total_q
        avg_time = self.total_time / total_q if total_q > 0 else 0
        speed_score = max(0, 1 - (avg_time / 6))  # 6s per answer is neutral
        final_score = round((accuracy * 0.7 + speed_score * 0.3) * 100)

        results = QtWidgets.QLabel(
            f"Test complete\n\nCorrect: {self.correct_count} / {total_q}\n"
            f"Total time: {self.total_time:.1f} sec\n"
            f"Avg. time per question: {avg_time:.1f} sec\n"
            f"Re-score: {final_score}/100"
        )
        results.setStyleSheet("font: 18px; color: white;")
        results.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(results)

        try_again_btn = QtWidgets.QPushButton("Try Again")
        try_again_btn.setStyleSheet("font: 16px; background-color: #2D2D2D; color: white; border-radius: 5px; padding: 8px;")
        try_again_btn.clicked.connect(lambda: self.start_with_words(self.source_words))
        self.layout.addWidget(try_again_btn)
