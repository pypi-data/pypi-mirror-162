from io import BytesIO


def generate_global_package_index(package_names):
    index_html = BytesIO()
    index_html.write(b"<!DOCTYPE html><html><head></head><body>\n")
    for packagename in package_names:
        index_html.write(
            f"""<a href="/simple/{packagename}/">{packagename}</a>""".encode("utf-8")
        )

    index_html.write(b"</body></html>")
    index_html.seek(0)
    return index_html


def generate_package_files_index(package_name, paths):
    index_html = BytesIO()
    index_html.write(b"<!DOCTYPE html><html><head></head><body>\n")
    for path in paths:
        filename = path.split("/")[-1]
        index_html.write(f"""<a href="{path}">{filename}</a><br>""".encode("utf-8"))

    index_html.write(b"</body></html>")
    index_html.seek(0)
    return index_html
