from injectable import injectable


@injectable
class UtilsString:
    def remove_mixed_spaces(self, text: str) -> str:
        words = text.split(' ')
        new_words = [word.strip() for word in words if len(word.strip()) > 0]
        return ' '.join(new_words)
