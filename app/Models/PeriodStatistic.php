<?php

declare(strict_types=1);

namespace FireflyIII\Models;

use FireflyIII\Casts\SeparateTimezoneCaster;
use FireflyIII\Support\Models\ReturnsIntegerUserIdTrait;
use Illuminate\Database\Eloquent\Casts\Attribute;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\MorphTo;

class PeriodStatistic extends Model
{
    use ReturnsIntegerUserIdTrait;

    protected function casts(): array
    {
        return [
            'created_at'    => 'datetime',
            'updated_at'    => 'datetime',
            'start'         => SeparateTimezoneCaster::class,
            'end'           => SeparateTimezoneCaster::class,
        ];
    }

    public function userGroup(): BelongsTo
    {
        return $this->belongsTo(UserGroup::class);
    }

    protected function count(): Attribute
    {
        return Attribute::make(
            get: static fn ($value) => (int)$value,
        );
    }

    public function primaryStatable(): MorphTo
    {

        return $this->morphTo();

    }

    public function secondaryStatable(): MorphTo
    {

        return $this->morphTo();

    }

    public function tertiaryStatable(): MorphTo
    {

        return $this->morphTo();

    }
}
