import {AbsoluteFill, Sequence} from "remotion";
import {
  getSceneStartFrames,
  getSegmentDurationInFrames,
  lessonSchema,
  type Lesson,
} from "./lesson";
import {LessonScene} from "./scenes";

export const LessonComposition = (props: Lesson) => {
  const lesson = lessonSchema.parse(props);
  const starts = getSceneStartFrames(lesson);

  return (
    <AbsoluteFill>
      {lesson.segments.map((segment, index) => (
        <Sequence
          key={segment.id}
          from={starts[index]}
          durationInFrames={getSegmentDurationInFrames(segment)}
        >
          <LessonScene
            segment={segment}
            reducedMotion={lesson.reducedMotion}
          />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
