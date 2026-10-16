baseline = 'E:/AI项目/光权修复_论文工作包_2026-06-03/07_模型与候选方案/对照光照复核模型/baseline_original_full_site.skp'
output = 'E:/AI项目/光权修复_论文工作包_2026-06-03/07_模型与候选方案/对照光照复核模型/algorithm_after_full_site_only_C6_C33_changed.skp'

def walk_entities(entities, &block)
  entities.each do |entity|
    block.call(entity)
    if entity.respond_to?(:definition) && entity.definition
      walk_entities(entity.definition.entities, &block)
    elsif entity.respond_to?(:entities)
      walk_entities(entity.entities, &block)
    end
  end
end

def entity_matches_building?(entity, building_id)
  names = []
  names << entity.name if entity.respond_to?(:name)
  names << entity.definition.name if entity.respond_to?(:definition) && entity.definition
  names.compact.any? do |name|
    !!(name =~ /(^|[^A-Za-z0-9])#{building_id}(_|[^A-Za-z0-9]|$)/)
  end
end

begin
  Sketchup.open_file(baseline)
  model = Sketchup.active_model

  # Give SketchUp a moment to finish loading component definitions.
  UI.start_timer(1.0, false) do
    begin
      model = Sketchup.active_model
      model.start_operation('AI conservative C6 C33 height reduction', true)
      changed = []
      targets = { 'C6' => 0.75, 'C33' => 0.75 }

      walk_entities(model.entities) do |entity|
        next unless entity.is_a?(Sketchup::Group) || entity.is_a?(Sketchup::ComponentInstance)

        targets.each do |building_id, scale_z|
          next unless entity_matches_building?(entity, building_id)

          entity.make_unique if entity.respond_to?(:make_unique)
          bounds = entity.bounds
          base = Geom::Point3d.new(bounds.center.x, bounds.center.y, bounds.min.z)
          transform = Geom::Transformation.scaling(base, 1.0, 1.0, scale_z)
          entity.transform!(transform)
          label = entity.name.to_s.empty? && entity.respond_to?(:definition) ? entity.definition.name : entity.name
          changed << "#{building_id}: #{label}"
          break
        end
      end

      model.commit_operation
      model.save(output)
      File.write(output.sub(/\.skp$/, '_changed_groups.txt'), changed.uniq.join("\n"))
      UI.messagebox("AI algorithm-after SKP saved:\n#{output}\n\nChanged groups:\n#{changed.uniq.join("\n")}")
    rescue => e
      File.write(output.sub(/\.skp$/, '_error.txt'), "#{e.class}: #{e.message}\n#{e.backtrace.join("\n")}")
      UI.messagebox("Failed to create algorithm-after SKP:\n#{e.class}: #{e.message}")
    end
  end
rescue => e
  File.write(output.sub(/\.skp$/, '_startup_error.txt'), "#{e.class}: #{e.message}\n#{e.backtrace.join("\n")}")
  UI.messagebox("Startup failed:\n#{e.class}: #{e.message}")
end
