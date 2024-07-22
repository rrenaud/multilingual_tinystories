import tarfile
import json
import os
import hashlib


class StoryJsonCombiner:
    def __init__(self):
        self.buffered_output = []
        self.num_outputs = 0
        self.seen_md5s = set()
    
    def _write_buffered_outputs(self):
        if not self.buffered_output:
            return
        print('writing output', self.num_outputs)
        with open(f'spanish_stories/stories_{self.num_outputs:02d}.json', 'w') as fp:
            json.dump(self.buffered_output, fp)
        self.num_outputs += 1
        self.buffered_output = []

    def add_story(self, story_dict):
        md5 = hashlib.md5(story_dict['story'].encode()).hexdigest()
        if md5 in self.seen_md5s:         
            print('skipping duplicate story')           
            return
        self.seen_md5s.add(md5)
        self.buffered_output.append(story_dict)
        if len(self.buffered_output) >= 100000:
            self._write_buffered_outputs()        


def tarfile_story_iterator(tarfile_path):
    with tarfile.open(tarfile_path, 'r:gz') as tar:
        for member in tar.getmembers():
            if member.isfile():
                f = tar.extractfile(member)
                try:
                    story = json.load(f)
                except Exception as e:
                    print('Error loading json', e, ' in', member.name)
                    continue
                yield story

def tarfiles_story_iterator(tarfile_dir):
    for fn in os.listdir(tarfile_dir):
        if not fn.endswith('.tar.gz'):
            continue
        for story in tarfile_story_iterator(tarfile_dir + fn):
            yield story

def raw_json_story_iterator(json_dir):
    for fn in os.listdir(json_dir):
        if not fn.endswith('.json'):
            continue
        with open(json_dir + '/' + fn) as fp:
            try:
                story = json.load(fp)
            except Exception as e:
                print('Error loading json', e, ' in', fn)
                continue
            yield story


def main():
    output_combiner = StoryJsonCombiner()
    # story_source = tarfiles_story_iterator('/home/rrenaud/work/')
    story_source = raw_json_story_iterator('/home/rrenaud/multilingual_tinystories/spanish_stories_translated')
    for story in story_source:
        output_combiner.add_story(story)

    output_combiner._write_buffered_outputs()
    print('saw', len(output_combiner.seen_md5s), 'unique stories')
    print('wrote', output_combiner.num_outputs, 'output files')
        
    


if __name__ == '__main__':
    main()
    