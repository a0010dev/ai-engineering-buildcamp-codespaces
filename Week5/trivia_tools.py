import html
import requests



class TriviaTools(object):
    def get_categories(self) -> str:
        """Get all available trivia categories with their IDs."""
        url = "https://opentdb.com/api_category.php"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()

        lines = []
        for cat in data['trivia_categories']:
            lines.append(f"{cat['id']}: {cat['name']}")

        return "\n".join(lines)

    def get_questions(self, amount: int, category: int, difficulty: str) -> str:
        """Fetch trivia questions.

        Args:
            amount: Number of questions (1-10)
            category: Category ID (use get_categories to see options)
            difficulty: easy, medium, or hard
        """
        params = {
            'amount': amount,
            'category': category,
            'difficulty': difficulty,
            'type': 'multiple',
        }
        url = "https://opentdb.com/api.php"
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        lines = []
        for i, q in enumerate(data['results'], 1):
            question = html.unescape(q['question'])
            correct = html.unescape(q['correct_answer'])
            wrong = [html.unescape(a) for a in q['incorrect_answers']]
            lines.append(f"Question {i}: {question}")
            lines.append(f"  Correct answer: {correct}")
            lines.append(f"  Wrong answers: {', '.join(wrong)}")
            lines.append("")

        return "\n".join(lines)    



if __name__ == '__main__':

    from trivia_tools import TriviaTools
    tools = TriviaTools()
    print(tools.get_categories())


