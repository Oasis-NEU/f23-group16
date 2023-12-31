from src.slots.sheet_parser import insert_sheet_into_db, parse_sheet
from src.server.server import create_app


def main() -> None:
    app = create_app()

    with app.app_context():
        insert_sheet_into_db(parse_sheet())

    app.run(debug=True, host='0.0.0.0', port=4000)


if __name__ == '__main__':
    main()
