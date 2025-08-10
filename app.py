import os
from flask import Flask, render_template, request, jsonify
from database import db, init_db, QueryLog
from scraper import fetch_case_details # <--- UNCOMMENT THIS LINE

def create_app():
    app = Flask(__name__)
    
    # Initialize the database
    init_db(app)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/search_case', methods=['POST'])
    def search_case():
        data = request.get_json()
        case_type = data.get('caseType')
        case_number = data.get('caseNumber')
        filing_year = data.get('filingYear')

        if not all([case_type, case_number, filing_year]):
            return jsonify({'success': False, 'message': 'Missing case details.'}), 400

        raw_scrape_response = None
        status = 'ERROR'
        error_msg = None
        case_data = {} # This will hold the parsed data

        try:
            # --- REPLACE PLACEHOLDER WITH ACTUAL SCRAPER CALL ---
            case_data, raw_scrape_response, scraper_error_msg = fetch_case_details(case_type, case_number, filing_year)
            
            if scraper_error_msg:
                error_msg = scraper_error_msg
                message = f'Failed to fetch case details: {error_msg}'
                status = 'ERROR'
            elif case_data.get('parties') is None and case_data.get('filingDate') is None:
                 # If basic data is still None, it probably means "Case Not Found" or failed to parse
                 error_msg = "Case details could not be found or parsed. Please check the input or try again."
                 message = error_msg
                 status = 'ERROR'
            else:
                status = 'SUCCESS'
                message = 'Case details fetched successfully.'
            # --- END OF SCRAPER INTEGRATION ---

        except Exception as e:
            error_msg = str(e)
            message = f'An unexpected error occurred during scraping: {error_msg}'
            status = 'ERROR'

        # Log the query to the database
        new_log = QueryLog(
            case_type=case_type,
            case_number=case_number,
            filing_year=int(filing_year),
            raw_response=raw_scrape_response,
            status=status,
            error_message=error_msg
        )
        db.session.add(new_log)
        db.session.commit()

        if status == 'SUCCESS':
            return jsonify({'success': True, 'message': message, **case_data})
        else:
            # Use 500 for server-side errors, 400 for client errors like missing data
            return jsonify({'success': False, 'message': message, 'error': error_msg}), 500 


    return app

if __name__ == '__main__':p
    app = create_app()
    app.run(debug=True) # Run in debug mode for development