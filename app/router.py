from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

routes = {
    "faq": [
        "What is the return policy of the products?",
        "Do I get a discount with the HDFC Credit Card?",
        "How can I track my order?",
        "Can I pay cash?",
        "What payment methods are accepted?",
        "How long does it take to process a refund?",
        "What are your delivery charges?",
        "Do you ship internationally?",
        "How do I cancel my order?",
        "What is your exchange policy?",
        "Is there a warranty on the products?",
        "Can I return a product without the original packaging?",
        "How can I contact customer service?",
        "Do you offer gift wrapping?",
        "Are there any membership benefits?",
        "Can I change my shipping address after ordering?",
        "How long does it take to receive a refund?",
        "What is your return policy for electronics?",
        "Do you offer COD (cash on delivery)?",
        "What are the terms and conditions for sale items?",
        "Are there any hidden charges?",
        "Can I use multiple promo codes?",
        "Is my personal data secure with your website?",
        "Do you accept international credit cards?",
        "How do I apply a discount coupon?",
        "Can I get an invoice for my order?"
    ],
    "sql": [
        "I want to buy Nike shoes that have 50% discount.",
        "Are there any shoes under Rs. 3000?",
        "Do you have formal shoes in size 9?",
        "Are there any Puma shoes on sale?",
        "What is the price of Puma running shoes?",
        "Show me black formal shoes under 3000",
        "I’m looking for discounted sports shoes",
        "Do you have Reebok sneakers on sale?",
        "Is there anything in size 8 and under 2500?",
        "What are the cheapest running shoes available?",
        "Do you sell Skechers casual shoes?",
        "Can I find red sneakers for men?",
        "What’s the best deal on Adidas shoes?",
        "Show me latest arrivals in women’s footwear",
        "Do you have waterproof boots?",
        "Looking for leather shoes under 4000",
        "Can you show me size 10 sandals on sale?",
        "Are slip-on shoes available in stock?",
        "Do you sell hiking shoes?",
        "I want shoes for formal occasions",
        "Find me trail running shoes under 5000",
        "Looking for lightweight walking shoes",
        "Do you have flip flops in size 7?",
        "What are the newest arrivals in men's shoes?",
        "Can I get white sneakers under 3500?"
    ]
}

model = SentenceTransformer("paraphrase-MiniLM-L6-v2")  # ~80MB model

route_embeddings = {
    route: model.encode(utterances) for route, utterances in routes.items()
}

def route_query(query, threshold=0.55):
    query_vec = model.encode([query])
    best_score = -1
    best_route = None
    for route, embeddings in route_embeddings.items():
        sim = cosine_similarity(query_vec, embeddings)
        max_sim = np.max(sim)
        if max_sim > best_score:
            best_score = max_sim
            best_route = route
    return best_route if best_score >= threshold else "none"

# Test
print(route_query("What would I do if you were not there?"))
print(route_query("Looking for white Adidas sneakers under 4000"))
print(route_query("Do you accept SBI credit cards?"))
print(route_query(" Looking for blue Adidas sneakers under 5000"))

print(route_query("Can I use a debit card for payment?"))                 # → faq
print(route_query("Is there a way to contact your support team?"))       # → faq
print(route_query("Do you give refunds on returned items?"))             # → faq
print(route_query("What are your customer support hours?"))              # → faq
print(route_query("Can I change my delivery location after I place an order?"))  # → faq

print(route_query("Show me red running shoes under 6000"))              # → sql
print(route_query("I need waterproof sneakers for hiking"))             # → sql
print(route_query("Do you have size 11 loafers in stock?"))             # → sql
print(route_query("Are there any formal black shoes on sale?"))         # → sql
print(route_query("Looking for casual sandals under 2000 rupees"))

print(route_query("You're my favorite chatbot"))                         # → none
print(route_query("Tell me something interesting"))                      # → none
print(route_query("How’s the weather today?"))                           # → none
print(route_query("Who created you?"))                                   # → none
print(route_query("Do you think machines will take over the world?"))   # → none

