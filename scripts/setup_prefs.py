import argparse
import json
import db_helper

def main():
    parser = argparse.ArgumentParser(description="Setup user preferences")
    parser.add_argument("--set-genres", type=str, help="Comma-separated list of genre IDs")
    parser.add_argument("--set-platforms", type=str, help="Comma-separated list of platform IDs")
    parser.add_argument("--set-include-watched", type=str, help="Set include_watched preference (true/false)")
    parser.add_argument("--set-min-year", type=str, help="Set minimum release year (e.g., 2010), or pass 'none' to clear")
    parser.add_argument("--view", action="store_true", help="View current preferences")
    args = parser.parse_args()

    conn = db_helper.get_connection()
    cursor = conn.cursor()

    if args.set_genres:
        genre_list = [int(x.strip()) for x in args.set_genres.split(',') if x.strip()]
        cursor.execute(
            "INSERT OR REPLACE INTO prefs (key, value) VALUES (?, ?)",
            ('genres', json.dumps(genre_list))
        )
        conn.commit()
        print(json.dumps({"success": True, "message": "Genres updated", "genres": genre_list}))

    if args.set_platforms:
        platform_list = [int(x.strip()) for x in args.set_platforms.split(',') if x.strip()]
        cursor.execute(
            "INSERT OR REPLACE INTO prefs (key, value) VALUES (?, ?)",
            ('platforms', json.dumps(platform_list))
        )
        conn.commit()
        print(json.dumps({"success": True, "message": "Platforms updated", "platforms": platform_list}))

    if args.set_include_watched is not None:
        val_bool = args.set_include_watched.lower() in ('true', '1', 'yes')
        cursor.execute(
            "INSERT OR REPLACE INTO prefs (key, value) VALUES (?, ?)",
            ('include_watched', json.dumps(val_bool))
        )
        conn.commit()
        print(json.dumps({"success": True, "message": "include_watched updated", "include_watched": val_bool}))
        
    if args.set_min_year is not None:
        if args.set_min_year.lower() == 'none':
            cursor.execute("DELETE FROM prefs WHERE key = ?", ('min_year',))
            conn.commit()
            print(json.dumps({"success": True, "message": "min_year cleared"}))
        else:
            try:
                year = int(args.set_min_year)
                cursor.execute(
                    "INSERT OR REPLACE INTO prefs (key, value) VALUES (?, ?)",
                    ('min_year', json.dumps(year))
                )
                conn.commit()
                print(json.dumps({"success": True, "message": "min_year updated", "min_year": year}))
            except ValueError:
                print(json.dumps({"success": False, "error": "Invalid min_year format. Must be integer or 'none'."}))

    if args.view or (not args.set_genres and not args.set_platforms and args.set_include_watched is None and args.set_min_year is None):
        prefs = db_helper.get_prefs(conn)
        print(json.dumps(prefs, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
