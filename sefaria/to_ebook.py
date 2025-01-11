import subprocess

def to_ebook(input_file, output_file, comments, tags,
            level1_toc="//h:h1", level2_toc="//h:h2", level3_toc="//h:h3"):
    subprocess.run(["ebook-convert",input_file, output_file, f"comments={comments}",f"tags={tags}", 
                    f"level1-toc={level1_toc}" ,f"level2-toc={level2_toc}" ,f"level3-toc={level3_toc}"])