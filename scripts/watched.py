import argparse
import json
import datetime
import db_helper

def main():
    parser = argparse.ArgumentParser(description="Manage watched titles")
    parser.add_argument("--flag", nargs='+', metavar=('TMDB_ID', 'TITLE'), help="Mark a title as watched")
    parser.add_argument("--unflag", type=int, metavar='TMDB_ID', help="Unmark a title as watched")
    parser.add_argument("--list", action="store_true", help="List all watched titles")
    args = parser.parse_args()

    conn = db_helper.get_connection()
    cursor = conn.cursor()

    if args.flag:
        if len(args.flag) < 2:
            print(json.dumps({"error": "You must provide both tmdb_id and title to flag a movie."}))
            return
            
        try:
            tmdb_id = int(args.flag[0])
            title = ' '.join(args.flag[1:])
        except ValueError:
            print(json.dumps({"error": "tmdb_id must be an integer."}))
            return
            
        now = datetime.datetime.utcnow().isoformat()
        cursor.execute(
            "INSERT OR REPLACE INTO watched (tmdb_id, title, flagged_at) VALUES (?, ?, ?)",
            (tmdb_id, title, now)
        )
        conn.commit()
        print(json.dumps({"success": True, "message": f"'{title}' marked as watched."}))

    elif args.unflag:
        tmdb_id = args.unflag
        cursor.execute("DELETE FROM watched WHERE tmdb_id = ?", (tmdb_id,))
        conn.commit()
        print(json.dumps({"success": True, "message": f"ID {tmdb_id} unmarked as watched."}))

    elif args.list:
        cursor.execute("SELECT tmdb_id, title, flagged_at FROM watched ORDER BY flagged_at DESC")
        rows = cursor.fetchall()
        
        output = []
        for row in rows:
            output.append({
                "id": row["tmdb_id"],
                "title": row["title"],
                "flagged_at": row["flagged_at"]
            })
            
        print(json.dumps(output, indent=2, ensure_ascii=False))
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
