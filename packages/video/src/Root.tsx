import fixture from "../fixtures/binary-search.json";
import {type CalculateMetadataFunction, Composition} from "remotion";
import {LessonComposition} from "./LessonComposition";
import {
  FPS,
  getDurationInFrames,
  lessonSchema,
  type Lesson,
} from "./lesson";

const defaultLesson = lessonSchema.parse(fixture);

const calculateMetadata: CalculateMetadataFunction<Lesson> = ({props}) => {
  const lesson = lessonSchema.parse(props);

  return {
    durationInFrames: getDurationInFrames(lesson),
    props: lesson,
  };
};

export const RemotionRoot = () => (
  <Composition
    id="Lesson"
    component={LessonComposition}
    durationInFrames={getDurationInFrames(defaultLesson)}
    fps={FPS}
    width={1280}
    height={720}
    defaultProps={defaultLesson}
    schema={lessonSchema}
    calculateMetadata={calculateMetadata}
  />
);
