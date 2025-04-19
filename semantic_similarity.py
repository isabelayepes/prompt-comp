from sentence_transformers import SentenceTransformer, util, CrossEncoder
from anthropic import Anthropic
from dotenv import load_dotenv
import os

load_dotenv()

client = Anthropic() # anthropic SDK automatically looks for an environment variable called "ANTHROPIC_API_KEY"

def compute_feature_cosine_similarity(text1, text2):
    # Load SBERT model
    model = SentenceTransformer('all-MiniLM-L6-v2')  # You can change this to other SBERT models

    # Encode the texts to get their embeddings
    emb1 = model.encode(text1, convert_to_tensor=True)
    emb2 = model.encode(text2, convert_to_tensor=True)

    # Compute cosine similarity
    similarity = util.pytorch_cos_sim(emb1, emb2)

    return similarity.item()


def compute_cross_encoder_similarity(text1: str, text2: str) -> float:
    # Load pre-trained Cross-Encoder model
    model = CrossEncoder('cross-encoder/stsb-roberta-base')  # You can use other CrossEncoder models too

    # Predict similarity score between 0 and 5
    score = model.predict([(text1, text2)])  # Must be a list of pairs

    return float(score[0])

def get_claude_similarity_score(text1: str, text2: str) -> str:
    prompt = f"""
                Rate the semantic similarity between the following two texts on a scale from 1 to 10:
                (1 = Not similar at all, 10 = Very similar in meaning)

                Text 1: "{text1}"
                Text 2: "{text2}"

                Respond with only a single number between 1 and 10.
              """

    response = client.messages.create(
        model="claude-3-haiku-20240307",  # or "opus", "sonnet" based on your tier
        max_tokens=10,
        temperature=0,
        system="You are an expert in semantic similarity and NLP.",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text.strip()


if __name__ == "__main__":
    # Example texts
    text1 = "A group of friends are planning a trip to the mountains."
    text2 = "Several people are organizing a vacation in the hills."

    score1 = compute_feature_cosine_similarity(text1, text2)
    score2 = compute_cross_encoder_similarity(text1, text2)
    score3 = get_claude_similarity_score(text1, text2)

    print(f"Cosine similarity score: {score1:.4f}")
    print(f"Cross-Encoder score: {score2:.4f}")
    print(f"Claude similarity score (0-10): {score3}")
