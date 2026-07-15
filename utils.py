PATH = 'data/topics_list.txt'
def read_students_from_file(filename: str) -> list:
    '''Read file, convert its content tolist
      and return list of students'''
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            students = f.read().split('\n')
    except FileNotFoundError as e:
        students = []
        print(f"File {filename} not found. Created empty topics list.")
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    return students

def read_topics_from_file(filename: str) -> list[dict]:
    """
    Reads topic data from a text file and parses it into a list of dictionaries.
    
    The file is expected to contain one topic per line, with each line formatted
    as: 'name; topic_type; max_score'. Empty lines and lines that do not match
    this exact format (not having exactly 3 semicolon-separated parts) are skipped.
    
    Args:
        filename (str): The path to the file to be read.
        
    Returns:
        list[dict]: A list of dictionaries, where each dictionary represents a topic
                    with the keys 'topic_name', 'topic_type', and 'topic_max_score'.
                    Returns an empty list if the file is not found or errors occur.
                    
    Raises:
        Handles FileNotFoundError, ValueError, and general Exceptions internally
        by printing an error message and returning an empty or partially filled list.
    """
    topics_list = []
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.read().strip().split('\n')      
            for line in lines:
                if not line.strip(): 
                    continue 
                parts = line.split('; ')
                if len(parts) != 3:
                    print(f"Skipping line (invalid format): {line}")
                    continue
                name, topic_type, max_score = parts
                topic_dict = {
                    'topic_name': name.strip(),
                    'topic_type': topic_type.strip().lower(),
                    'topic_max_score': int(max_score.strip())
                }
                topics_list.append(topic_dict)
        print(f"Loaded {len(topics_list)} topics from file.")
        
    except FileNotFoundError:
        print(f"File {filename} not found. Created empty topics list.")
    except ValueError as e:
        print(f"Data conversion error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    return topics_list

if __name__ == '__main__':
    topics = read_topics_from_file(PATH)
    print(topics)