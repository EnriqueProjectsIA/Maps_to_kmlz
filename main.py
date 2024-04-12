import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List
import logger
from datetime import datetime as dt
import warnings
from termcolor import colored


def parse_from_text_to_float(input:List[str])->List[float]:
    """
    Parse a list of strings to a list of integers.

    Parameters:
    - input: List of strings to be parsed.

    Returns:
    - List of integers.
    """
    return [float(i) for i in input]

def parse_list_float_to_str(input:List[float])->List[str]:
    """
    Parse a list of floats to a list of strings.

    Parameters:
    - input: List of floats to be parsed.

    Returns:
    - List of strings.
    """
    out_put = ''
    for i in input:
        out_put += f"{i},"
    return out_put[:-1]

def parse_kml(kml_path, use_logger:bool = False)->Dict[str, Dict[str, List[float]]]:
    """
    Parses a KML file to extract information about points of interest and lines,
    including names and coordinates, using xml.etree.ElementTree.

    :param kml_path: Path to the KML file.
    :return: None
    """
    if use_logger:
        file_name = str(Path(kml_path).name).split('.')[0]
        path = Path(__file__).parent / "logs"
        path.mkdir(exist_ok=True)
        now = dt.now().strftime("%Y-%m-%d_%H-%M-%S")
        path = path / f"{now}_{file_name}.log"
        logger_object = logger.configure_logger(name = file_name, path=path)

    # Namespace used in KML files
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    
    tree = ET.parse(kml_path)
    root = tree.getroot()
    
    output_dict = {
        'points': {},
        'route': {}
    }
    for pm in root.findall('.//kml:Placemark', ns):
        name = pm.find('kml:name', ns).text if pm.find('kml:name', ns) is not None else "Unnamed"
        # Check for Points
        point = pm.find('.//kml:Point/kml:coordinates', ns)
        if point is not None:
            if use_logger:
                logger_object.info(f"Point of Interest: {name}, Coordinates: {point.text.strip()}")
            try:
                output_dict['points'][name] = [float(i) for i in point.text.strip().split(',')][:-1] #Remove the altitude
            except Exception as e:
                if use_logger:
                    logger_object.error(f"Error while parsing coordinates for {name}: {e}")
                warnings.warn(colored(f"Error while parsing coordinates for {name}: {e}", "red"))
            continue
        # Check for Lines
        line = pm.find('.//kml:LineString/kml:coordinates', ns)
        if line is not None:
            if use_logger:
                logger_object.info(f"Line: {name}, Coordinates: {line.text.strip()}")
            try:
                output_dict['route'][name] = [parse_from_text_to_float(i.strip().split(',')[:-1][::-1]) for i in line.text.strip().split('\n')] #Remove the altitude
            except Exception as e:
                if use_logger:
                    logger_object.error(f"Error while parsing coordinates for {name}: {e}")
                warnings.warn(colored(f"Error while parsing coordinates for {name}: {e}", "red"))
    return output_dict

def transform_dict_to_csvs(input:Dict, target_key:str = 'route', output_directory:str|None = None)->None:
    """
    Transform a dictionary to CSV files.

    Parameters:
    - input: Dictionary to be transformed.

    Returns:
    - None
    """
    if output_directory is None:
        output_directory = Path(__file__).parent / "output_data"
    if not output_directory.exists():
        output_directory.mkdir()
    objective_dict = input[target_key]
    for key, value in objective_dict.items():
        key = key.replace(" ", "_").lower()
        output_path = output_directory / f"{key}.csv"
        output_path = str(output_path.resolve())
        with open(output_path, "w") as f:
            f.write("Latitud,Longitud\n")
            for item in value:
                f.write(f"{parse_list_float_to_str(item)}\n")

def wrapper(path_to_directory:str|None = None, file_name:str|None = None, use_logger:bool = False)->None:
    """
    Wrapper function to parse a KML file and transform the output to CSV files.

    Returns:
    - None
    """
    if path_to_directory is None:
        path_to_directory = Path(__file__).parent / "input_data"
    else:
        path_to_directory = Path(path_to_directory)
    if not path_to_directory.exists():
        raise FileNotFoundError(f"Directory {path_to_directory} not found.")
    
    if file_name is None:
        file_name = path_to_directory.glob("*.kml")
        file_name = [i for i in file_name if i.is_file()]
        if len(file_name) == 0 or len(file_name) > 1:
            raise FileNotFoundError(f"Expected 1 KML file in {path_to_directory}, found {len(file_name)} files.")
        file_name = file_name[0]
    else:
        file_name = Path(file_name)
        if not file_name.exists():
            raise FileNotFoundError(f"File {file_name} not found.")
    
    full_path = path_to_directory / file_name
    full_path = str(full_path.resolve())
    
    out_put = parse_kml(full_path, use_logger=use_logger)
    transform_dict_to_csvs(out_put)

# Example usage
if __name__ == "__main__":  
    wrapper(use_logger=True)

