import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.Random;

public class ImmediatePost {

    private static final String TELEGRAM_TOKEN = "8461091151:AAEd-mqGswAijmwFB0teeXeZFe-gtHfD-PI";
    private static final String TELEGRAM_CHANNEL_ID = "-1002201089739";
    private static final String GOOGLE_API_KEY = "AIzaSyCuWBy5qkUMO5oTAcIivzYSC0R9xiZjoUU";

    public static void main(String[] args) throws Exception {
        // Пример списка трендов (замена google trends API на статический список для простоты)
        String[] trends = {"тренды в маркетинге 2025", "новые функции Telegram", "AI в рекламе"};
        Random random = new Random();
        String selectedTrend = trends[random.nextInt(trends.length)];
        System.out.println("Выбран тренд: " + selectedTrend);

        String prompt = "Напиши короткий остроумный пост для Telegram-канала на тему '" + selectedTrend + "'.";

        // Генерация текста через Gemini API (HTTP POST)
        String generatedText = generateTextGemini(prompt);
        System.out.println("Сгенерированный текст: " + generatedText);

        // Отправка сообщения в Telegram
        sendTelegramMessage(generatedText);
    }

    private static String generateTextGemini(String prompt) throws Exception {
        HttpClient client = HttpClient.newHttpClient();

        String apiUrl = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateText?key=" + GOOGLE_API_KEY;

        String jsonPayload = "{"
                + "\"prompt\": {\"text\": \"" + prompt + "\"},"
                + "\"maxOutputTokens\": 256"
                + "}";

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(apiUrl))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(jsonPayload))
                .build();

        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());

        if (response.statusCode() == 200) {
            // Для простоты парсим ответ вручную (лучше использовать JSON библиотеку, например, Jackson/Gson)
            String body = response.body();
            int start = body.indexOf("\"text\":\"") + 8;
            int end = body.indexOf("\"", start);
            if (start > 7 && end > start) {
                String text = body.substring(start, end);
                return text.replace("\\n", "\n").replace("\\\"", "\"");
            }
            return "Ошибка парсинга ответа.";
        } else {
            throw new RuntimeException("Ошибка запроса Gemini API: " + response.statusCode() + " " + response.body());
        }
    }

    private static void sendTelegramMessage(String text) throws Exception {
        HttpClient client = HttpClient.newHttpClient();

        String url = "https://api.telegram.org/bot" + TELEGRAM_TOKEN + "/sendMessage";

        String jsonPayload = "{"
                + "\"chat_id\": \"" + TELEGRAM_CHANNEL_ID + "\","
                + "\"text\": \"" + text.replace("\"", "\\\"") + "\","
                + "\"parse_mode\": \"HTML\""
                + "}";

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(jsonPayload))
                .build();

        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
        if (response.statusCode() == 200) {
            System.out.println("Пост успешно отправлен в Telegram");
        } else {
            throw new RuntimeException("Ошибка отправки Telegram: " + response.statusCode() + " " + response.body());
        }
    }
}
