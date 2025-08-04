from flask import Flask, request, jsonify, render_template
import boto3
from botocore.exceptions import ClientError
from decimal import Decimal

app = Flask(__name__)

# Direct DynamoDB connection with hardcoded credentials (TESTING ONLY)
dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id='',
    aws_secret_access_key='',
    region_name='us-east-2'
)

# DynamoDB table setup
table_name = 'Books'  # Ensure your table name is correct
table = dynamodb.Table(table_name)

@app.route('/')
def home():
    return render_template('index.html')  # Optional: ensure templates/index.html exists

@app.route('/add_book', methods=['POST'])
def add_book():
    data = request.get_json()
    writer = data.get('writer')
    book = data.get('book')
    price = data.get('price')

    if not all([writer, book, price]):
        return jsonify({'error': 'Missing fields'}), 400

    try:
        # Use lowercase keys to match your DynamoDB table
        table.put_item(Item={
            'writer': writer,
            'book': book,
            'price': Decimal(str(price))  # Decimal for DynamoDB
        })
        return jsonify({'message': 'Book added successfully'})
    except ClientError as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_book', methods=['GET'])
def get_book():
    writer = request.args.get('writer')
    book = request.args.get('book')

    if not all([writer, book]):
        return jsonify({'error': 'Missing writer or book'}), 400

    try:
        response = table.get_item(Key={
            'writer': writer,
            'book': book
        })
        item = response.get('Item')
        if item:
            return jsonify(item)
        else:
            return jsonify({'message': 'Book not found'}), 404
    except ClientError as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
